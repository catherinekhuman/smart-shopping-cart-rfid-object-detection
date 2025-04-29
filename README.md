# Smart Shopping Cart with RFID and Object Detection

## Features:

- **RFID-Based Product Detection**: Automatically logs items added to the cart using RFID tags and an MFRC-522 reader.
- **Object Detection & Following**: Uses YOLOv3-tiny and OpenCV to detect and follow the user throughout the store.
- **Automated Billing**: Live item tracking and QR-code-based checkout  
- **Real-Time Inventory Sync**: Dual-database system with Firebase and MariaDB keeps product stock accurate in real-time.
- **Autonomous Navigation**: Raspberry Pi and L298N motor driver enable the cart to follow the user hands-free.

  
## Technologies Used:

- Raspberry Pi 4 Model B
- RFID (MFRC-522) + Tags
- Raspberry Pi Camera Module V2
- Python, OpenCV, Flask, Firebase, MariaDB
