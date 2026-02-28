#!/bin/bash
# This is called by the udev kernel rule when a USB is inserted.
# It creates the trigger file that the SCRAM Brain is watching.
echo "USB_PANIC" > /tmp/.scram_panic
