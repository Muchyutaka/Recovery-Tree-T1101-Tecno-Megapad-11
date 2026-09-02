#!/usr/bin/env bash
# No recovery-source patches are applied anymore.
#
# The old patch redirected the TWRP/OrangeFox haptics sysfs path to
# /sys/class/leds/vibrator_single - that is the XPad (X1101) aw862xx driver,
# which the T1101 does not have. The T1101 uses the standard
# /sys/class/leds/vibrator path, i.e. the unpatched source is correct.
#
# Patching bootable/recovery from here also breaks OrangeFox builds, where
# bootable/recovery is the OrangeFox fork and the patch does not apply.
export LC_ALL="C"
