'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _lodash = require('lodash.kebabcase');

var _lodash2 = _interopRequireDefault(_lodash);

var _lodash3 = require('lodash.camelcase');

var _lodash4 = _interopRequireDefault(_lodash3);

var _lodash5 = require('lodash.snakecase');

var _lodash6 = _interopRequireDefault(_lodash5);

var _pascalcase = require('pascalcase');

var _pascalcase2 = _interopRequireDefault(_pascalcase);

var _lodash7 = require('lodash.isstring');

var _lodash8 = _interopRequireDefault(_lodash7);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var langTransforms = {
  kebab: _lodash2.default,
  camel: _lodash4.default,
  snake: _lodash6.default,
  pascal: _pascalcase2.default
};

var isValidOption = function isValidOption(opt) {
  return opt && (0, _lodash8.default)(opt);
};
var validTranform = function validTranform(opt) {
  return Object.keys(langTransforms).indexOf(opt) > -1;
};

var checkValidOptions = function checkValidOptions(state) {
  var attribute = 'data-qa';
  var format = 'kebab';

  if (isValidOption(state.opts.attribute)) {
    attribute = state.opts.attribute;
  }

  if (isValidOption(state.opts.format) && validTranform(state.opts.format)) {
    format = state.opts.format;
  }

  return {
    format: langTransforms[format],
    attribute: attribute
  };
};

exports.default = checkValidOptions;