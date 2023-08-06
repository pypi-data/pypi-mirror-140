#!/bin/bash
#
# Verify that 'hello_bdev' runs using bdev/xNVMe using NVMe device
#
# In the environment / testplan define the io-interface to use:
#
# XNVME_ASYNC={io_uring,io_uring_cmd,libaio,emu,thrpool}
#
# It uses the script 'spdk_bdevconf_create.py' to create a bdev-configuration
#
# shellcheck disable=SC2119
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

: "${XNVME_ASYNC:?Must be set and non-empty}"

cij.info "Using bdev-configuration:"
if ! cij.cmd "cat ${SPDK_BDEV_CONFIG}"; then
  test.fail
fi

#if ! cij.cmd "${SPDK_REPOS}/build/examples/hello_bdev -L xnvme -b bdev_xnvme -c ${SPDK_BDEV_CONFIG}"; then
if ! cij.cmd "${SPDK_REPOS}/build/examples/hello_bdev -b bdev_auto -c ${SPDK_BDEV_CONFIG}"; then
  test.fail "failing running 'hello_bdev'"
fi

test.pass
