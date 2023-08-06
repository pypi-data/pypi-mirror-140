#!/usr/bin/env bash
#
# kmemleak module, providing helpers to: "clear", "scan" and "cat" kmemleak
#
# For details on kmemleak, have a look at the Linux Kernel Documentation at
#
# https://www.kernel.org/doc/html/latest/dev-tools/kmemleak.html
#
kmemleak.env() {
  if ! ssh.env; then
    cij.err "kmemleak.env - Invalid SSH ENV."
    return 1
  fi

  return 0;
}

kmemleak.cat() {
  if ! kmemleak.env; then
    cij.err "kmemleak.env - invalid kmemleak ENV."
    return 1
  fi

  cij.cmd "cat /sys/kernel/debug/kmemleak"
}

kmemleak.scan() {
  if ! kmemleak.env; then
    cij.err "kmemleak.env - invalid kmemleak ENV."
    return 1
  fi

  cij.cmd "echo scan > /sys/kernel/debug/kmemleak"
}

kmemleak.clear() {
  if ! kmemleak.env; then
    cij.err "kmemleak.env - invalid kmemleak ENV."
    return 1
  fi

  cij.cmd "echo clear > /sys/kernel/debug/kmemleak"
}
