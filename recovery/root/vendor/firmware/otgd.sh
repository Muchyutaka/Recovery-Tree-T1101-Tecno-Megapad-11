#!/system/bin/sh
# otg host mode helper for the T1101.
# tran_otg gates vbus on a plug-in flag that never gets set in recovery,
# and the tcpc attach routine knocks the boost back off right after plug
# in. so we watch the kernel log and keep re-asserting otg + host role
# until it sticks. log: /tmp/otgd.log

VER=otgd-v5.1
OTG_CTL=/sys/devices/platform/odm/odm:tran_battery/OTG_CTL
ROLE=/sys/class/usb_role/mt_usb-role-switch/role
LOGF=/tmp/otgd.log
FLAG=/tmp/otgd_on

log() {
    echo "$(date +%H:%M:%S) $VER: $1" >> "$LOGF" 2>/dev/null
    echo "<6>$VER: $1" > /dev/kmsg 2>/dev/null
}

: > "$LOGF" 2>/dev/null
rm -f "$FLAG" 2>/dev/null
log "started (pid $$)"

i=0
while [ "$i" -lt 180 ]; do
    [ -w "$OTG_CTL" ] && [ -e "$ROLE" ] && break
    sleep 1
    i=$((i + 1))
done
if [ ! -w "$OTG_CTL" ] || [ ! -e "$ROLE" ]; then
    log "giving up after ${i}s: nodes missing"
    exit 0
fi
log "nodes ready after ${i}s"

# ---------- keeper: re-assert while the flag exists ----------
(
    beat=0
    while :; do
        if [ -e "$FLAG" ]; then
            echo 1 > "$OTG_CTL" 2>/dev/null
            [ "$(cat "$ROLE" 2>/dev/null)" = "host" ] || echo host > "$ROLE" 2>/dev/null
            beat=$((beat + 1))
            if [ $((beat % 20)) = "0" ]; then
                log "alive state=1"
            fi
        fi
        sleep 1
    done
) &
KEEPER=$!

# ---------- listener: live kernel message tap ----------
cat /dev/kmsg 2>/dev/null | while IFS= read -r line; do
    case "$line" in
        *"source vbus = 5000mv"*)
            if [ ! -e "$FLAG" ]; then
                touch "$FLAG"
                # host role first so the first enumeration attempt is not lost
                echo host > "$ROLE" 2>>"$LOGF"
                echo 1 > "$OTG_CTL" 2>>"$LOGF"
                log "OTG ON (ctl=$(cat "$OTG_CTL" 2>/dev/null) role=$(cat "$ROLE" 2>/dev/null))"
                # ride out the tcpc knock-off
                (
                    j=0
                    while [ "$j" -lt 8 ]; do
                        sleep 0.25
                        [ -e "$FLAG" ] || break
                        echo 1 > "$OTG_CTL" 2>/dev/null
                        j=$((j + 1))
                    done
                ) &
            fi
            ;;
        *"Type-C SRC plug in"*|*"pd_tcp_notifier_call OTG plug in"*)
            # attach routine knocks the boost off, put it right back
            if [ -e "$FLAG" ]; then
                echo 1 > "$OTG_CTL" 2>/dev/null
            fi
            ;;
        *"source vbus = 0mv"*|*"Charger plug in"*)
            if [ -e "$FLAG" ]; then
                rm -f "$FLAG"
                echo device > "$ROLE" 2>>"$LOGF"
                echo 0 > "$OTG_CTL" 2>>"$LOGF"
                log "OTG OFF"
            fi
            ;;
    esac
done

kill "$KEEPER" 2>/dev/null

# ---------- fallback: poll dmesg if the kmsg tap dies ----------
log "kmsg tap ended, falling back to dmesg polling"
state=0
while :; do
    last=$(dmesg 2>/dev/null | grep 'source vbus' | grep -v otgd | tail -1)
    case "$last" in
        *'= 5000mv'*) want=1 ;;
        *)            want=0 ;;
    esac
    if [ "$want" = "1" ]; then
        if [ "$state" != "1" ]; then
            touch "$FLAG"; state=1
            echo host > "$ROLE" 2>/dev/null
            log "OTG ON"
        fi
        echo 1 > "$OTG_CTL" 2>/dev/null
        [ "$(cat "$ROLE" 2>/dev/null)" = "host" ] || echo host > "$ROLE" 2>/dev/null
    else
        if [ "$state" = "1" ]; then
            rm -f "$FLAG"; state=0
            echo device > "$ROLE" 2>/dev/null
            echo 0 > "$OTG_CTL" 2>/dev/null
            log "OTG OFF"
        fi
    fi
    sleep 1
done
