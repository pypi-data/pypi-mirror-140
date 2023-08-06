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

hook.linux_nvme_enter() {

  NVME_MODULE_ARGS=""
  if [[ "$LINUX_NVME_POLL" -eq 1 ]]; then
      NVME_MODULE_ARGS="$NVME_MODULE_ARGS poll_queues=1"
  fi

  if ! cij.cmd "rmmod nvme"; then
    cij.err "hook.linux_nvme_enter: FAILED: detaching NVMe driver"
    return 1
  fi

  if ! cij.cmd "modprobe nvme $NVME_MODULE_ARGS"; then
    cij.err "hook.linux_nvme_enter: FAILED: Attaching NVMe driver with poll queues"
    return 1
  fi

  return 0
}

hook.linux_nvme_enter
exit $?
