'use strict';

// const mock = {};
// 
// require('fs').readdirSync(require('path').join(__dirname + '/mock'))
//   .forEach(function (file) {
//     if(!file.startsWith('.')) {
//       Object.assign(mock, require('./mock/' + file));
//     }
//   });
// 
// module.exports = mock;


export default {
    // Forward 到另一个服务器
    'GET /api*': 'http://127.0.0.1:5000',
}
