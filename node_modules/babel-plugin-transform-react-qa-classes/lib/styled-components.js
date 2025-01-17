'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = TaggedTemplateExpression;

var _path3 = require('path');

var _path = _interopRequireWildcard(_path3);

var _babelTypes = require('babel-types');

var t = _interopRequireWildcard(_babelTypes);

var _options = require('./options');

var _options2 = _interopRequireDefault(_options);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function TaggedTemplateExpression(path, state) {
  var options = (0, _options2.default)(state);
  var scope = path.scope;

  try {
    // simple case
    if (isStyledPrefix(path.node.tag)) {
      var id = getIdFrom(path.parentPath);
      if (!id) return;
      path.node.tag = insertBefore(path.node.tag, id);
      return;
    }

    // chained case.  traverse until prefix found.
    // NB: styled-component chain api is always CallExpression+MemberExpression pairs.
    var node = path.node.tag;
    while (true) {
      if (!node || !node.callee) break;
      if (isStyledPrefix(node.callee.object)) {
        var _id = getIdFrom(path.parentPath);
        if (!_id) return;
        node.callee.object = insertBefore(node.callee.object, _id);
        break;
      }
      node = node.callee.object;
    }
  } catch (e) {}

  // hoisted helpers in closure
  function insertBefore(node, id) {
    return t.callExpression(t.memberExpression(node, t.identifier('attrs')), [t.objectExpression([t.objectProperty(t.StringLiteral(options.attribute), t.StringLiteral(options.format(id)))])]);
  }
  function isStyledPrefix(node) {
    // handle two forms: styled.div and styled(Comp)
    return t.isMemberExpression(node) && isStyledComponentsBinding(node.object) || t.isCallExpression(node) && isStyledComponentsBinding(node.callee);
    function isStyledComponentsBinding(node) {
      if (!t.isIdentifier(node)) return false;
      var binding = scope.getBinding(node.name);
      if (!binding || binding.kind !== 'module') return false;
      return binding.path.parent.source.value === 'styled-components';
    }
  }
  function getIdFrom(parentPath) {
    if (t.isVariableDeclarator(parentPath.node)) {
      return parentPath.node.id.name;
    }
    if (t.isArrowFunctionExpression(parentPath.node)) {
      if (t.isVariableDeclarator(parentPath.parentPath.node)) {
        return parentPath.parentPath.node.id.name;
      }
    }
    if (t.isExportDefaultDeclaration(parentPath.node)) {
      var _path2 = state.file.opts.filename;
      var filename = _path.parse(_path2).name;
      if (filename === 'index') {
        var parent = _path.basename(_path.dirname(filename));
        return parent;
      }
      return filename;
    }
  }
}