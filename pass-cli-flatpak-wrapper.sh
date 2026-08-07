#!/bin/bash

set -o pipefail

KEY="$(secret-tool lookup application pass-cli-flatpak-wrapper)"

if [ $? -ne 0 ]; then
	head -c 32 /dev/urandom \
		| base64 -w 0 \
		| secret-tool store --label=pass-cli-flatpak-wrapper application pass-cli-flatpak-wrapper \
		|| exit 1
	KEY="$(secret-tool lookup application pass-cli-flatpak-wrapper)" || exit 1
fi

export PROTON_PASS_KEY_PROVIDER=env
export PROTON_PASS_ENCRYPTION_KEY="$KEY"
exec -a pass-cli /app/bin/.pass-cli-wrapped "$@"
