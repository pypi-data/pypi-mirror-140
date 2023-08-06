#!/usr/bin/env bash
#
# SPDK info describing the test-target;
# Define where SPDK and fio are located
#
SPDK_REPOS="/opt/spdk"; export SPDK_REPOS
# Used by the bdev-configuration generator
SPDK_BDEV_FILENAME="/dev/nvme0n1"; export SPDK_BDEV_FILENAME
SPDK_BDEV_BS="512"; export SPDK_BDEV_BS
# This file-name is used on the dev-box s well as the test-target
SPDK_BDEV_CONFIG="/tmp/spdk_bdev_config.json"; export SPDK_BDEV_CONFIG

# The external fio io-engines depend on the fio-version on which they built against. So, we set the
# FIO_BIN to point it to a non-default location
FIO_BIN="/opt/fio/fio"; export FIO_BIN
