# dpswitch
GUI application for fast switching between different multi-monitor configurations.

# Motivation

I have two desktop system with each two displays, a primary and secondary monitor. On each system, the primary monitor has higher resolution and refresh rate than the secondary. Because of the different monitor specification, my graphics cards (Geforce GTX 1060 and Radeon RX 580) have problems running the most power efficient mode. If they can't run at the lowest power, both systems consume 20 W more in idle. So, it is not the best idea to have both monitors constantly running at the highest refresh rate. With this tool, different monitor configurations can be setup for different workflows and activate with a single button click.

The tool allows to create a different number of configurations, so called mods. In my case, I have defined the following modes:

* **Powersafe:** Run only the primary display at 60 Hz. Good for daily work such as writing e-mails and surfing. The lowest power consumption is guaranteed.
* **Gaming:** Run only the primary display with highest possible Hz. Proton works really well ;-)
* **Multi-Monitor:** Run the primary and secondary display. Good for work, e.g. developing.

## Power Measurement

The following table shows the power consumption of my systems with different display configurations in idle.

* System 1:
  * Geforce GTX 1060
  * Primary Display (PDp): 2560x1440@165Hz
  * Secondary Display (SDp): 1920x1080@60Hz
* System 2:
  * Radeon RX 580
  * Primary Display (PDp): 1920x1080@144Hz
  * Secondary Display (SDp): 1280x1024@60Hz

|          | PDp@60Hz | PDp@144Hz | PDp@165Hz | PDp@60Hz + SDp@60Hz | PDp@144Hz + SDp@60Hz |
| -------- | -------- | --------- | --------- | ------------------- |  ------------------- |
| System 1 | 60 W     | 60 W      | 80 W      | 60 W                | 80 W                 |
| System 2 | 70 W     | 90 W      | -         | 90 W                | 90 W                 |

# Requirements

* Linux
* Python >3.6
* PyQt5 >5.9

# Usage

Simply run the script `dpswitch.py` and the GUI will start. The default path of the config json is `/etc/dpswitch/config.json`. If you want to use a custom path to the json file, run `./dpswitch.py </path/to/config.json`.

# Creating a config

With the command `xrandr` you get all the information you need for the config.json. The basic structure of the json is:

```json
{
	"displays" : {
		<display name 1> : {
			"port" : <DP-x|HDMI-x|VGA-x|DVI-x>
		}
	},
	"configs" : {
		<mode name> :
		{
			"display" : <display name 1>,
			"resolution" : <widthxheight>,
			"rate" : <refresh rate>
		},
		<mode 2 name> :
		{
			"display" : <display name 1>,
			"resolution" : <widthxheight>,
			"rate" : <refresh rate>
		}
	}
}
```

Optional attributes are `primary` to set the primary monitor and `postion` to set the position of a second display.

```json
{
	"displays" : {
		<display name 1> : {
			"port" : <DP-x|HDMI-x|VGA-x|DVI-x>
		}
	},
	"configs" : {
		<mode name> :
		{
			"display" : <display name 1>,
			"resolution" : <widthxheight>,
			"rate" : <refresh rate>,
			"primary" : true,
			"position" : [<left|right|above|below>, <display name of the relative display>]
		}
	}
}
```

For multi-display setups it is necessary to define more than one display for a mode. Instead of a dict with the attributes for the display, you can use a list of dicts.

```json
{
	"displays" : {
		<display name 1> : {
			"port" : <DP-x|HDMI-x|VGA-x|DVI-x>
		},
		<display name 2> : {
			"port" : <DP-x|HDMI-x|VGA-x|DVI-x>
		}
	},
	"configs" : {
		<mode name> :
		[
			{
				"display" : <display name 1>,
				"resolution" : <widthxheight>,
				"rate" : <refresh rate>,
				"primary" : true,
			},
			{
				"display" : <display name 2>,
				"resolution" : <widthxheight>,
				"rate" : <refresh rate>,
				"position" : [<left|right|above|below>, <display name of the relative display>]
			}
		]
	}
}
```

In `example.json`, you can find a configuration of my system.
