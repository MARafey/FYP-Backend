const os = require('os');

// Processor Information
const processorName = os.cpus()[0].model;
const logicalCores = os.cpus().length;
const totalRAM = (os.totalmem() / (1024 ** 3)).toFixed(2);

console.log(`Processor: ${processorName}`);
console.log(`Logical Cores: ${logicalCores}`);
console.log(`Total RAM: ${totalRAM} GB`);
