#!/usr/bin/env bash
#
# Enable/ disable poll queue for the linux nvme driver
#
# on-enter: Enable poll queue
# on-exit:  Disable poll queue
#
CIJ_TEST_NAME=$(basename "${BASH_SOURCE[0]}")
export CIJ_TEST_NAME
# shellcheck source=modules/cijoe.sh
source "$CIJ_ROOT/modules/cijoe.sh"
test.enter

hook.linux_nvme_exit() {

  if ! cij.cmd "rmmod nvme"; then
    cij.err "hook.linux_nvme_exit: FAILED: detaching NVMe driver"
    return 1
  fi

  if ! cij.cmd "modprobe nvme"; then
    cij.err "hook.linux_nvme_exit: FAILED: Attaching NVMe driver without poll queues"
    return 1
  fi

  return 0
}

hook.linux_nvme_exit
exit $?
