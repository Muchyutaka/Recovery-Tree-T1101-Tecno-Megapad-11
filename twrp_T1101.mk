#
# Copyright (C) 2022 The LineageOS Project
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit tecno T1101 device stuff
$(call inherit-product, device/tecno/T1101/T1101.mk)

# Inherit some common TWRP stuff.
$(call inherit-product, vendor/twrp/config/common.mk)

# Product Specifics
PRODUCT_NAME := twrp_T1101
PRODUCT_DEVICE := T1101
PRODUCT_BRAND := tecno
PRODUCT_MODEL := tecno T1101
PRODUCT_MANUFACTURER := tecno

PRODUCT_GMS_CLIENTID_BASE := android-tecno
