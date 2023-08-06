#!/usr/bin/env bash
#
# Verifies that environment variables required by the SPDK testcases are
# defined and detaches / re-attaches NVMe devices from kernel to user space
#
# on-enter: de-attach from kernel NVMe driver
# on-exit: re-attach to kernel NVMe driver
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

hook.spdk_bdev_conf_enter() {
  if ! spdk.env; then
    cij.err "spdk.env - Invalid SPDK env."
    return 1
  fi

  # Generate bdev-configuration, transfer it to the test-target, and print it for checking
  spdk_bdevconf_create.py \
    --filename "${SPDK_BDEV_FILENAME}" \
    --be_async "${XNVME_ASYNC}" \
    --bs "${SPDK_BDEV_BS}" > "${SPDK_BDEV_CONFIG}"

  if ! cij.push "${SPDK_BDEV_CONFIG}" "${SPDK_BDEV_CONFIG}"; then
    test.fail "FAILED: pushing bdev-config($SPDK_BDEV_CONFIG)";
  fi

  return 0
}

hook.spdk_bdev_conf_enter
exit $?
