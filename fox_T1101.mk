#
# Copyright (C) 2022 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

$(call inherit-product, device/tecno/T1101/T1101.mk)

$(call inherit-product-if-exists, vendor/fox/config/common.mk)

# Product Specifics
PRODUCT_NAME := fox_T1101
PRODUCT_DEVICE := T1101
PRODUCT_BRAND := TECNO
PRODUCT_MODEL := Tecno MegaPad 11
PRODUCT_MANUFACTURER := tecno

PRODUCT_GMS_CLIENTID_BASE := android-transsion

# OrangeFox flags
FOX_MAINTAINER_PATCH_VERSION := 1
FOX_BUILD_TYPE := Unofficially
OF_KEEP_FORCED_ENCRYPTION := true
OF_DISABLE_MIUI_SPECIFIC_FEATURES := true
FOX_VIRTUAL_AB_DEVICE := 1

BUILD_FINGERPRINT := TECNO/TSSI/T1101:14/UP1A.231005.007/260410V1046:user/release-keys
PRODUCT_BUILD_PROP_OVERRIDES += \
    TARGET_DEVICE=T1101 \
    PRODUCT_NAME=T1101 \
    PRIVATE_BUILD_DESC="sys_tssi_64_armv82_tecno_dolby-user 14 UP1A.231005.007 987287 release-keys"
