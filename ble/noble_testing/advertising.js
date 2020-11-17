var noble = require('@abandonware/noble');
var my_address = "f0-5c-d5-db-26-a8";

noble.on('stateChange', function (state) {
  if (state === 'poweredOn') {
    noble.startScanning();
  } else {
    noble.stopScanning();
  }
});

noble.on('discover', function (peripheral) {

  if (peripheral.address === my_address) {
    console.log("YAY\n\n");
    console.log(`peripheral discovered (${peripheral.id} with address <${peripheral.address}, ${peripheral.addressType}>, connectable ${peripheral.connectable}, RSSI ${peripheral.rssi}:`);
    console.log('\thello my local name is:');
    console.log(`\t\t${peripheral.advertisement.localName}`);
    console.log('\tcan I interest you in any of the following advertised services:');
    console.log(`\t\t${JSON.stringify(peripheral.advertisement.serviceUuids)}`);

    const serviceData = peripheral.advertisement.serviceData;
    if (serviceData && serviceData.length) {
      console.log('\there is my service data:');
      for (const i in serviceData) {
        console.log(`\t\t${JSON.stringify(serviceData[i].uuid)}: ${JSON.stringify(serviceData[i].data.toString('hex'))}`);
      }
    }
    if (peripheral.advertisement.manufacturerData) {
      console.log('\there is my manufacturer data:');
      console.log(`\t\t${JSON.stringify(peripheral.advertisement.manufacturerData.toString('hex'))}`);
    }
    if (peripheral.advertisement.txPowerLevel !== undefined) {
      console.log('\tmy TX power level is:');
      console.log(`\t\t${peripheral.advertisement.txPowerLevel}`);
    }

    console.log();
  } else {
    console.log(peripheral.address);
    console.log();
  }

});

// function onDiscovery(peripheral) {
//   // peripheral.rssi                             - signal strength
//   // peripheral.address                          - MAC address
//   // peripheral.advertisement.localName          - device's name
//   // peripheral.advertisement.manufacturerData   - manufacturer-specific data
//   // peripheral.advertisement.serviceData        - normal advertisement service data
//   // ignore devices with no manufacturer data
  

//   if (!peripheral.advertisement.manufacturerData) return;
//   // output what we have
//   console.log(
//     peripheral.address,
//     JSON.stringify(peripheral.advertisement.localName),
//     JSON.stringify(peripheral.advertisement.manufacturerData)
//   );
// }

// noble.on('stateChange',  function(state) {
//   if (state!="poweredOn") return;
//   console.log("Starting scan...");
//   noble.startScanning([], true);
// });
// noble.on('discover', onDiscovery);
// noble.on('scanStart', function() { console.log("Scanning started."); });
// noble.on('scanStop', function() { console.log("Scanning stopped.");});

// // // Read the battery level of the first found peripheral exposing the Battery Level characteristic

// // const noble = require('@abandonware/noble');

// // noble.on('stateChange', async (state) => {
// //   if (state === 'poweredOn') {
// //     await noble.startScanningAsync(['180f'], false);
// //   }
// // });

// // noble.on('discover', async (peripheral) => {
// //   await noble.stopScanningAsync();
// //   await peripheral.connectAsync();
// //   const {characteristics} = await peripheral.discoverSomeServicesAndCharacteristicsAsync(['180f'], ['2a19']);
// //   const batteryLevel = (await characteristics[0].readAsync())[0];

// //   console.log(`${peripheral.address} (${peripheral.advertisement.localName}): ${batteryLevel}%`);

// //   await peripheral.disconnectAsync();
// //   process.exit(0);
// // });

// var noble = require('@abandonware/noble');

// // List of allowed devices
// const devices = [
//   "c0:98:e5:49:12:34"
// ];
// // last advertising data received
// var lastAdvertising = {
// };

// function onDeviceChanged(addr, data) {
//   console.log("Device ",addr,"changed data",JSON.stringify(data));
// }

// function onDiscovery(peripheral) {
//   // do we know this device?
//   if (devices.indexOf(peripheral.address)<0) return;
//   // does it have manufacturer data with Espruino/Puck.js's UUID
//   if (!peripheral.advertisement.manufacturerData ||
//       peripheral.advertisement.manufacturerData[0]!=0x90 ||
//       peripheral.advertisement.manufacturerData[1]!=0x05) return;
//   // get just our data
//   var data = peripheral.advertisement.manufacturerData.slice(2);
//   // check for changed services
//   if (lastAdvertising[peripheral.address] != data.toString())
//     onDeviceChanged(peripheral.address, data);
//   lastAdvertising[peripheral.address] = data;
// }

// noble.on('stateChange',  function(state) {
//   if (state!="poweredOn") return;
//   console.log("Starting scan...");
//   noble.startScanning([], true);
// });
// noble.on('discover', onDiscovery);
// noble.on('scanStart', function() { console.log("Scanning started."); });
// noble.on('scanStop', function() { console.log("Scanning stopped.");});