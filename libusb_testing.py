
from pathlib import Path
from usb.core import find  # this is from pyusb
from usb.backend.libusb1 import get_backend

# backend = get_backend(find_library=Path("libusb-1.0.dylib"))
backend = get_backend(find_library="/Users/vincentdavis/REPO/vpower/libusb-1.0.dylib")
# print(backend)

f = find(backend=backend, find_all=True)
# f = find(find_all=True)
