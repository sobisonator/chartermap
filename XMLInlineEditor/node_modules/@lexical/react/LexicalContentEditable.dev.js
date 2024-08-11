/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';

var LexicalComposerContext = require('@lexical/react/LexicalComposerContext');
var react = require('react');
var jsxRuntime = require('react/jsx-runtime');
var text = require('@lexical/text');
var utils = require('@lexical/utils');

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const CAN_USE_DOM = typeof window !== 'undefined' && typeof window.document !== 'undefined' && typeof window.document.createElement !== 'undefined';

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */


// This workaround is no longer necessary in React 19,
// but we currently support React >=17.x
// https://github.com/facebook/react/pull/26395
const useLayoutEffectImpl = CAN_USE_DOM ? react.useLayoutEffect : react.useEffect;

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */
// Source: https://github.com/gregberge/react-merge-refs/blob/main/src/index.tsx

function mergeRefs(...refs) {
  return value => {
    refs.forEach(ref => {
      if (typeof ref === 'function') {
        ref(value);
      } else if (ref != null) {
        ref.current = value;
      }
    });
  };
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function ContentEditableElementImpl({
  editor,
  ariaActiveDescendant,
  ariaAutoComplete,
  ariaControls,
  ariaDescribedBy,
  ariaExpanded,
  ariaLabel,
  ariaLabelledBy,
  ariaMultiline,
  ariaOwns,
  ariaRequired,
  autoCapitalize,
  className,
  id,
  role = 'textbox',
  spellCheck = true,
  style,
  tabIndex,
  'data-testid': testid,
  ...rest
}, ref) {
  const [isEditable, setEditable] = react.useState(editor.isEditable());
  const handleRef = react.useCallback(rootElement => {
    // defaultView is required for a root element.
    // In multi-window setups, the defaultView may not exist at certain points.
    if (rootElement && rootElement.ownerDocument && rootElement.ownerDocument.defaultView) {
      editor.setRootElement(rootElement);
    } else {
      editor.setRootElement(null);
    }
  }, [editor]);
  const mergedRefs = react.useMemo(() => mergeRefs(ref, handleRef), [handleRef, ref]);
  useLayoutEffectImpl(() => {
    setEditable(editor.isEditable());
    return editor.registerEditableListener(currentIsEditable => {
      setEditable(currentIsEditable);
    });
  }, [editor]);
  return /*#__PURE__*/jsxRuntime.jsx("div", {
    ...rest,
    "aria-activedescendant": isEditable ? ariaActiveDescendant : undefined,
    "aria-autocomplete": isEditable ? ariaAutoComplete : 'none',
    "aria-controls": isEditable ? ariaControls : undefined,
    "aria-describedby": ariaDescribedBy,
    "aria-expanded": isEditable && role === 'combobox' ? !!ariaExpanded : undefined,
    "aria-label": ariaLabel,
    "aria-labelledby": ariaLabelledBy,
    "aria-multiline": ariaMultiline,
    "aria-owns": isEditable ? ariaOwns : undefined,
    "aria-readonly": isEditable ? undefined : true,
    "aria-required": ariaRequired,
    autoCapitalize: autoCapitalize,
    className: className,
    contentEditable: isEditable,
    "data-testid": testid,
    id: id,
    ref: mergedRefs,
    role: isEditable ? role : undefined,
    spellCheck: spellCheck,
    style: style,
    tabIndex: tabIndex
  });
}
const ContentEditableElement = /*#__PURE__*/react.forwardRef(ContentEditableElementImpl);

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function canShowPlaceholderFromCurrentEditorState(editor) {
  const currentCanShowPlaceholder = editor.getEditorState().read(text.$canShowPlaceholderCurry(editor.isComposing()));
  return currentCanShowPlaceholder;
}
function useCanShowPlaceholder(editor) {
  const [canShowPlaceholder, setCanShowPlaceholder] = react.useState(() => canShowPlaceholderFromCurrentEditorState(editor));
  useLayoutEffectImpl(() => {
    function resetCanShowPlaceholder() {
      const currentCanShowPlaceholder = canShowPlaceholderFromCurrentEditorState(editor);
      setCanShowPlaceholder(currentCanShowPlaceholder);
    }
    resetCanShowPlaceholder();
    return utils.mergeRegister(editor.registerUpdateListener(() => {
      resetCanShowPlaceholder();
    }), editor.registerEditableListener(() => {
      resetCanShowPlaceholder();
    }));
  }, [editor]);
  return canShowPlaceholder;
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const ContentEditable = /*#__PURE__*/react.forwardRef(ContentEditableImpl);
function ContentEditableImpl(props, ref) {
  const {
    placeholder,
    editor__DEPRECATED,
    ...rest
  } = props;
  // editor__DEPRECATED will always be defined for non MLC surfaces
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const editor = editor__DEPRECATED || LexicalComposerContext.useLexicalComposerContext()[0];
  return /*#__PURE__*/jsxRuntime.jsxs(jsxRuntime.Fragment, {
    children: [/*#__PURE__*/jsxRuntime.jsx(ContentEditableElement, {
      editor: editor,
      ...rest,
      ref: ref
    }), placeholder != null && /*#__PURE__*/jsxRuntime.jsx(Placeholder, {
      editor: editor,
      content: placeholder
    })]
  });
}
function Placeholder({
  content,
  editor
}) {
  const showPlaceholder = useCanShowPlaceholder(editor);
  const [isEditable, setEditable] = react.useState(editor.isEditable());
  react.useLayoutEffect(() => {
    setEditable(editor.isEditable());
    return editor.registerEditableListener(currentIsEditable => {
      setEditable(currentIsEditable);
    });
  }, [editor]);
  if (!showPlaceholder) {
    return null;
  }
  let placeholder = null;
  if (typeof content === 'function') {
    placeholder = content(isEditable);
  } else if (content !== null) {
    placeholder = content;
  }
  if (placeholder === null) {
    return null;
  }
  return /*#__PURE__*/jsxRuntime.jsx("div", {
    "aria-hidden": true,
    children: placeholder
  });
}

exports.ContentEditable = ContentEditable;
