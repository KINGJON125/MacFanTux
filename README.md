# MacFanTux 

MacFanTux is a user-friendly GUI application for controlling MacBook fans on Linux. It allows you to manually adjust fan speeds by modifying the minimum speed values for `fan1` and `fan2` in:

```
/sys/devices/platform/applesmc.768/
```



## 📖 Story 
I switched to Linux and struggled to find a GUI-based fan control app similar to [Macs Fan Control](https://crystalidea.com/macs-fan-control) for Linux. Since none existed, I created MacFanTux!

## 💻 Supported Models
Tested on the **Late 2011 MacBook Pro (MacBookPro8,2)** and may work with every intel macbook.

## 📦 Installation (Will Improve in v1.0)
### Prerequisites
Ensure you have [Python](https://www.python.org/) installed on your system.

### Steps
#### Install Git
For Arch Linux:
```
sudo pacman -S git
```
For other distributions, use the appropriate package manager.

#### Clone the Repository
```
git clone https://github.com/KINGJON125/MacFanTux.git
```

#### Navigate to the Directory
```
cd MacFanTux
```

#### Install Dependencies
For Arch Linux:
```
sudo pacman -S psutil
```
For other distros:
```
pip3 install psutil
```

## 🚀 Usage
- The app provides sliders to control fan speeds.
- A **"FULL BLAST!!!"** button sets fans to maximum speed.
- Temperature sensors are displayed on the right side of the interface.
- how to run? 
```
sudo python3 main.py
```
as simple as that!
## ⚠ Common Issues
- **Sleep Mode Issue:** When the Mac goes to sleep, fan control settings may reset automatically.

---

🔧 *More improvements coming soon! Stay tuned for v1.0.*

