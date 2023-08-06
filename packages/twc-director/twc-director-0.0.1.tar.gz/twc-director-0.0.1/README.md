# Tesla Wall Charger Director

Python library for basic control of Tesla Wall Chargers in peripheral mode. Tesla Wall Charger protocol was reverse engineered largely from observing communication between a Tesla Wall Charger in controller mode and a Tesla Wall Charger in peripheral mode. The commands to increase/decrease session charge current and commands to open and close contactors were found on the very detailed Tesla Motors Club forum thread 

https://teslamotorsclub.com/tmc/threads/new-wall-connector-load-sharing-protocol.72830/

Thank you to everyone that contributed to that thread. 

The library does not currently implement any type of capacity sharing, it is assumed the maximum charge current is available to all chargers on the bus. There is no way for the library to check to make sure entered values are sane for a particular installation USE AT YOUR OWN RISK.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Library
An example of the library usage can be found in utility.py. A program can register for new device events and then register for command events that it is interested in. There is a special command event fired called "\_\_ALL_COMMANDS\_\_" that is fired for a device whenever a command has been decoded. The event "TWC_CAR_CONNECTED" is fired when all fragments of a VIN have been received and again when any fragment reverts to null.

## Command line
There is a utility mode that allows the library to be used from the command line. It provides reporting of peripheral activity and can be used to open-close contactors, set default and session charge current to a set of pre-defined values and incrementally increase or decrease charge current for an active charge session.

The utility or library can not be used to start or stop a charge session in a way that is resumeable. The Tesla wall chargers do not report battery capacity or state of charge.

From within the module directory, or after the module has been installed help for the utility can be found by running the following command.

```bash
pytho3 -m twcdirector.utility --help
```

Once appropriate options have been selected and the utility is up-and-running it can be exited by hitting CTRL-C which will perform a graceful shutdown.

The up and down arrow keys can be used to select a particular peripheral then the following commands can be sent to the selected peripheral.

| Key | Description |
| ------ | ------|
| d | Open contactors. This will typically put a connected car into an error state and it will need to be unplugged, plugged back in to clear the error |
| c | Close contactors. |
| 1 | Send a default current command of 6A. This has no effect after connection. |
| 2 | Send a default current command of 10A. This has no effect after connection. |
| 3 | Send a default current command of 20A. This has no effect after connection. |
| 4 | Send a default current command of 32A. This has no effect after connection. |
| 5 | Send a default current command of 0A. This is typically interpreted by the peripheral as 6A, just present for testing. |
| 6 | Send a session current command of 6A. This sets the limit for the current charge session, can only be used after car is connected. |
| 7 | Send a session current command of 10A. This sets the limit for the current charge session, can only be used after car is connected. |
| 8 | Send a session current command of 20A. This sets the limit for the current charge session, can only be used after car is connected. |
| 9 | Send a session current command of 32A. This sets the limit for the current charge session, can only be used after car is connected. |
| 0 | Send a session current command of 0A. This is typically interpreted by the peripheral as 6A, just present for testing. |
| - | Sends a decrease charge current command. This will only have an effect while charging is in progress. The peripheral alters charging current by a pre-defined amount. |
| + | Sends a increase charge current command. This will only have an effect while charging is in progress. The peripheral alters charging current by a pre-defined amount.  |

## Protocol Timing

Observations regarding protocol timing.

### Controller Discovery
| Command | Number | Interval | Notes |
| ------- |   ---: |     ---: | ----- |
| 0xE1    | 4      |   1300ms | Controller sends when first powered on then stops |

### Peripheral Presence
| Command | Interval  |  Notes |
| ------- |      ---: |  ----- |
| 0xE2    |    1300ms |  Peripheral keeps sending until a controller claims it |

### Peripheral request periods
The period seems to be a function of the total number of requests for data excluding the 0xE0 command. Intra command spacing is approximately 1300ms

| Command | Period  | Response Within | Notes |
| ------- |   ---:  |            ---: | ----- |
| 0xE0    | 1300ms  |           160ms | Controller requests status but does not report |
| 0xE2    | 200ms - 500ms |     160ms | Controller makes 3 requests on initial discovery then stops |        
| 0xEB    | 11800ms |           160ms | Controller reports using the same period |
| 0xEC    | 11800ms |           160ms | Controller reports using the same period |
| 0xED    | 11800ms |           160ms | Controller reports using the same period |
| 0xEE    | 11800ms |           160ms | Controller reports using the same period | 
| 0xEF    | 11800ms |           160ms | Controller reports using the same period |
| 0xF1    | 11800ms |           160ms | Controller reports using the same period | 



