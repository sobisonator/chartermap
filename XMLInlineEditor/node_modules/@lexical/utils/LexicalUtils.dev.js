/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';

var lexical = require('lexical');
var selection = require('@lexical/selection');

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const CAN_USE_DOM$1 = typeof window !== 'undefined' && typeof window.document !== 'undefined' && typeof window.document.createElement !== 'undefined';

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const documentMode = CAN_USE_DOM$1 && 'documentMode' in document ? document.documentMode : null;
const IS_APPLE$1 = CAN_USE_DOM$1 && /Mac|iPod|iPhone|iPad/.test(navigator.platform);
const IS_FIREFOX$1 = CAN_USE_DOM$1 && /^(?!.*Seamonkey)(?=.*Firefox).*/i.test(navigator.userAgent);
const CAN_USE_BEFORE_INPUT$1 = CAN_USE_DOM$1 && 'InputEvent' in window && !documentMode ? 'getTargetRanges' in new window.InputEvent('input') : false;
const IS_SAFARI$1 = CAN_USE_DOM$1 && /Version\/[\d.]+.*Safari/.test(navigator.userAgent);
const IS_IOS$1 = CAN_USE_DOM$1 && /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const IS_ANDROID$1 = CAN_USE_DOM$1 && /Android/.test(navigator.userAgent);

// Keep these in case we need to use them in the future.
// export const IS_WINDOWS: boolean = CAN_USE_DOM && /Win/.test(navigator.platform);
const IS_CHROME$1 = CAN_USE_DOM$1 && /^(?=.*Chrome).*/i.test(navigator.userAgent);
// export const canUseTextInputEvent: boolean = CAN_USE_DOM && 'TextEvent' in window && !documentMode;

const IS_ANDROID_CHROME$1 = CAN_USE_DOM$1 && IS_ANDROID$1 && IS_CHROME$1;
const IS_APPLE_WEBKIT$1 = CAN_USE_DOM$1 && /AppleWebKit\/[\d.]+/.test(navigator.userAgent) && !IS_CHROME$1;

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function normalizeClassNames(...classNames) {
  const rval = [];
  for (const className of classNames) {
    if (className && typeof className === 'string') {
      for (const [s] of className.matchAll(/\S+/g)) {
        rval.push(s);
      }
    }
  }
  return rval;
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

/**
 * Returns a function that will execute all functions passed when called. It is generally used
 * to register multiple lexical listeners and then tear them down with a single function call, such
 * as React's useEffect hook.
 * @example
 * ```ts
 * useEffect(() => {
 *   return mergeRegister(
 *     editor.registerCommand(...registerCommand1 logic),
 *     editor.registerCommand(...registerCommand2 logic),
 *     editor.registerCommand(...registerCommand3 logic)
 *   )
 * }, [editor])
 * ```
 * In this case, useEffect is returning the function returned by mergeRegister as a cleanup
 * function to be executed after either the useEffect runs again (due to one of its dependencies
 * updating) or the component it resides in unmounts.
 * Note the functions don't neccesarily need to be in an array as all arguments
 * are considered to be the func argument and spread from there.
 * The order of cleanup is the reverse of the argument order. Generally it is
 * expected that the first "acquire" will be "released" last (LIFO order),
 * because a later step may have some dependency on an earlier one.
 * @param func - An array of cleanup functions meant to be executed by the returned function.
 * @returns the function which executes all the passed cleanup functions.
 */
function mergeRegister(...func) {
  return () => {
    for (let i = func.length - 1; i >= 0; i--) {
      func[i]();
    }
    // Clean up the references and make future calls a no-op
    func.length = 0;
  };
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function px(value) {
  return `${value}px`;
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const mutationObserverConfig = {
  attributes: true,
  characterData: true,
  childList: true,
  subtree: true
};
function positionNodeOnRange(editor, range, onReposition) {
  let rootDOMNode = null;
  let parentDOMNode = null;
  let observer = null;
  let lastNodes = [];
  const wrapperNode = document.createElement('div');
  function position() {
    if (!(rootDOMNode !== null)) {
      throw Error(`Unexpected null rootDOMNode`);
    }
    if (!(parentDOMNode !== null)) {
      throw Error(`Unexpected null parentDOMNode`);
    }
    const {
      left: rootLeft,
      top: rootTop
    } = rootDOMNode.getBoundingClientRect();
    const parentDOMNode_ = parentDOMNode;
    const rects = selection.createRectsFromDOMRange(editor, range);
    if (!wrapperNode.isConnected) {
      parentDOMNode_.append(wrapperNode);
    }
    let hasRepositioned = false;
    for (let i = 0; i < rects.length; i++) {
      const rect = rects[i];
      // Try to reuse the previously created Node when possible, no need to
      // remove/create on the most common case reposition case
      const rectNode = lastNodes[i] || document.createElement('div');
      const rectNodeStyle = rectNode.style;
      if (rectNodeStyle.position !== 'absolute') {
        rectNodeStyle.position = 'absolute';
        hasRepositioned = true;
      }
      const left = px(rect.left - rootLeft);
      if (rectNodeStyle.left !== left) {
        rectNodeStyle.left = left;
        hasRepositioned = true;
      }
      const top = px(rect.top - rootTop);
      if (rectNodeStyle.top !== top) {
        rectNode.style.top = top;
        hasRepositioned = true;
      }
      const width = px(rect.width);
      if (rectNodeStyle.width !== width) {
        rectNode.style.width = width;
        hasRepositioned = true;
      }
      const height = px(rect.height);
      if (rectNodeStyle.height !== height) {
        rectNode.style.height = height;
        hasRepositioned = true;
      }
      if (rectNode.parentNode !== wrapperNode) {
        wrapperNode.append(rectNode);
        hasRepositioned = true;
      }
      lastNodes[i] = rectNode;
    }
    while (lastNodes.length > rects.length) {
      lastNodes.pop();
    }
    if (hasRepositioned) {
      onReposition(lastNodes);
    }
  }
  function stop() {
    parentDOMNode = null;
    rootDOMNode = null;
    if (observer !== null) {
      observer.disconnect();
    }
    observer = null;
    wrapperNode.remove();
    for (const node of lastNodes) {
      node.remove();
    }
    lastNodes = [];
  }
  function restart() {
    const currentRootDOMNode = editor.getRootElement();
    if (currentRootDOMNode === null) {
      return stop();
    }
    const currentParentDOMNode = currentRootDOMNode.parentElement;
    if (!(currentParentDOMNode instanceof HTMLElement)) {
      return stop();
    }
    stop();
    rootDOMNode = currentRootDOMNode;
    parentDOMNode = currentParentDOMNode;
    observer = new MutationObserver(mutations => {
      const nextRootDOMNode = editor.getRootElement();
      const nextParentDOMNode = nextRootDOMNode && nextRootDOMNode.parentElement;
      if (nextRootDOMNode !== rootDOMNode || nextParentDOMNode !== parentDOMNode) {
        return restart();
      }
      for (const mutation of mutations) {
        if (!wrapperNode.contains(mutation.target)) {
          // TODO throttle
          return position();
        }
      }
    });
    observer.observe(currentParentDOMNode, mutationObserverConfig);
    position();
  }
  const removeRootListener = editor.registerRootListener(restart);
  return () => {
    removeRootListener();
    stop();
  };
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function markSelection(editor, onReposition) {
  let previousAnchorNode = null;
  let previousAnchorOffset = null;
  let previousFocusNode = null;
  let previousFocusOffset = null;
  let removeRangeListener = () => {};
  function compute(editorState) {
    editorState.read(() => {
      const selection = lexical.$getSelection();
      if (!lexical.$isRangeSelection(selection)) {
        // TODO
        previousAnchorNode = null;
        previousAnchorOffset = null;
        previousFocusNode = null;
        previousFocusOffset = null;
        removeRangeListener();
        removeRangeListener = () => {};
        return;
      }
      const {
        anchor,
        focus
      } = selection;
      const currentAnchorNode = anchor.getNode();
      const currentAnchorNodeKey = currentAnchorNode.getKey();
      const currentAnchorOffset = anchor.offset;
      const currentFocusNode = focus.getNode();
      const currentFocusNodeKey = currentFocusNode.getKey();
      const currentFocusOffset = focus.offset;
      const currentAnchorNodeDOM = editor.getElementByKey(currentAnchorNodeKey);
      const currentFocusNodeDOM = editor.getElementByKey(currentFocusNodeKey);
      const differentAnchorDOM = previousAnchorNode === null || currentAnchorNodeDOM === null || currentAnchorOffset !== previousAnchorOffset || currentAnchorNodeKey !== previousAnchorNode.getKey() || currentAnchorNode !== previousAnchorNode && (!(previousAnchorNode instanceof lexical.TextNode) || currentAnchorNode.updateDOM(previousAnchorNode, currentAnchorNodeDOM, editor._config));
      const differentFocusDOM = previousFocusNode === null || currentFocusNodeDOM === null || currentFocusOffset !== previousFocusOffset || currentFocusNodeKey !== previousFocusNode.getKey() || currentFocusNode !== previousFocusNode && (!(previousFocusNode instanceof lexical.TextNode) || currentFocusNode.updateDOM(previousFocusNode, currentFocusNodeDOM, editor._config));
      if (differentAnchorDOM || differentFocusDOM) {
        const anchorHTMLElement = editor.getElementByKey(anchor.getNode().getKey());
        const focusHTMLElement = editor.getElementByKey(focus.getNode().getKey());
        // TODO handle selection beyond the common TextNode
        if (anchorHTMLElement !== null && focusHTMLElement !== null && anchorHTMLElement.tagName === 'SPAN' && focusHTMLElement.tagName === 'SPAN') {
          const range = document.createRange();
          let firstHTMLElement;
          let firstOffset;
          let lastHTMLElement;
          let lastOffset;
          if (focus.isBefore(anchor)) {
            firstHTMLElement = focusHTMLElement;
            firstOffset = focus.offset;
            lastHTMLElement = anchorHTMLElement;
            lastOffset = anchor.offset;
          } else {
            firstHTMLElement = anchorHTMLElement;
            firstOffset = anchor.offset;
            lastHTMLElement = focusHTMLElement;
            lastOffset = focus.offset;
          }
          const firstTextNode = firstHTMLElement.firstChild;
          if (!(firstTextNode !== null)) {
            throw Error(`Expected text node to be first child of span`);
          }
          const lastTextNode = lastHTMLElement.firstChild;
          if (!(lastTextNode !== null)) {
            throw Error(`Expected text node to be first child of span`);
          }
          range.setStart(firstTextNode, firstOffset);
          range.setEnd(lastTextNode, lastOffset);
          removeRangeListener();
          removeRangeListener = positionNodeOnRange(editor, range, domNodes => {
            for (const domNode of domNodes) {
              const domNodeStyle = domNode.style;
              if (domNodeStyle.background !== 'Highlight') {
                domNodeStyle.background = 'Highlight';
              }
              if (domNodeStyle.color !== 'HighlightText') {
                domNodeStyle.color = 'HighlightText';
              }
              if (domNodeStyle.zIndex !== '-1') {
                domNodeStyle.zIndex = '-1';
              }
              if (domNodeStyle.pointerEvents !== 'none') {
                domNodeStyle.pointerEvents = 'none';
              }
              if (domNodeStyle.marginTop !== px(-1.5)) {
                domNodeStyle.marginTop = px(-1.5);
              }
              if (domNodeStyle.paddingTop !== px(4)) {
                domNodeStyle.paddingTop = px(4);
              }
              if (domNodeStyle.paddingBottom !== px(0)) {
                domNodeStyle.paddingBottom = px(0);
              }
            }
            if (onReposition !== undefined) {
              onReposition(domNodes);
            }
          });
        }
      }
      previousAnchorNode = currentAnchorNode;
      previousAnchorOffset = currentAnchorOffset;
      previousFocusNode = currentFocusNode;
      previousFocusOffset = currentFocusOffset;
    });
  }
  compute(editor.getEditorState());
  return mergeRegister(editor.registerUpdateListener(({
    editorState
  }) => compute(editorState)), removeRangeListener, () => {
    removeRangeListener();
  });
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

// Hotfix to export these with inlined types #5918
const CAN_USE_BEFORE_INPUT = CAN_USE_BEFORE_INPUT$1;
const CAN_USE_DOM = CAN_USE_DOM$1;
const IS_ANDROID = IS_ANDROID$1;
const IS_ANDROID_CHROME = IS_ANDROID_CHROME$1;
const IS_APPLE = IS_APPLE$1;
const IS_APPLE_WEBKIT = IS_APPLE_WEBKIT$1;
const IS_CHROME = IS_CHROME$1;
const IS_FIREFOX = IS_FIREFOX$1;
const IS_IOS = IS_IOS$1;
const IS_SAFARI = IS_SAFARI$1;
/**
 * Takes an HTML element and adds the classNames passed within an array,
 * ignoring any non-string types. A space can be used to add multiple classes
 * eg. addClassNamesToElement(element, ['element-inner active', true, null])
 * will add both 'element-inner' and 'active' as classes to that element.
 * @param element - The element in which the classes are added
 * @param classNames - An array defining the class names to add to the element
 */
function addClassNamesToElement(element, ...classNames) {
  const classesToAdd = normalizeClassNames(...classNames);
  if (classesToAdd.length > 0) {
    element.classList.add(...classesToAdd);
  }
}

/**
 * Takes an HTML element and removes the classNames passed within an array,
 * ignoring any non-string types. A space can be used to remove multiple classes
 * eg. removeClassNamesFromElement(element, ['active small', true, null])
 * will remove both the 'active' and 'small' classes from that element.
 * @param element - The element in which the classes are removed
 * @param classNames - An array defining the class names to remove from the element
 */
function removeClassNamesFromElement(element, ...classNames) {
  const classesToRemove = normalizeClassNames(...classNames);
  if (classesToRemove.length > 0) {
    element.classList.remove(...classesToRemove);
  }
}

/**
 * Returns true if the file type matches the types passed within the acceptableMimeTypes array, false otherwise.
 * The types passed must be strings and are CASE-SENSITIVE.
 * eg. if file is of type 'text' and acceptableMimeTypes = ['TEXT', 'IMAGE'] the function will return false.
 * @param file - The file you want to type check.
 * @param acceptableMimeTypes - An array of strings of types which the file is checked against.
 * @returns true if the file is an acceptable mime type, false otherwise.
 */
function isMimeType(file, acceptableMimeTypes) {
  for (const acceptableType of acceptableMimeTypes) {
    if (file.type.startsWith(acceptableType)) {
      return true;
    }
  }
  return false;
}

/**
 * Lexical File Reader with:
 *  1. MIME type support
 *  2. batched results (HistoryPlugin compatibility)
 *  3. Order aware (respects the order when multiple Files are passed)
 *
 * const filesResult = await mediaFileReader(files, ['image/']);
 * filesResult.forEach(file => editor.dispatchCommand('INSERT_IMAGE', \\{
 *   src: file.result,
 * \\}));
 */
function mediaFileReader(files, acceptableMimeTypes) {
  const filesIterator = files[Symbol.iterator]();
  return new Promise((resolve, reject) => {
    const processed = [];
    const handleNextFile = () => {
      const {
        done,
        value: file
      } = filesIterator.next();
      if (done) {
        return resolve(processed);
      }
      const fileReader = new FileReader();
      fileReader.addEventListener('error', reject);
      fileReader.addEventListener('load', () => {
        const result = fileReader.result;
        if (typeof result === 'string') {
          processed.push({
            file,
            result
          });
        }
        handleNextFile();
      });
      if (isMimeType(file, acceptableMimeTypes)) {
        fileReader.readAsDataURL(file);
      } else {
        handleNextFile();
      }
    };
    handleNextFile();
  });
}

/**
 * "Depth-First Search" starts at the root/top node of a tree and goes as far as it can down a branch end
 * before backtracking and finding a new path. Consider solving a maze by hugging either wall, moving down a
 * branch until you hit a dead-end (leaf) and backtracking to find the nearest branching path and repeat.
 * It will then return all the nodes found in the search in an array of objects.
 * @param startingNode - The node to start the search, if ommitted, it will start at the root node.
 * @param endingNode - The node to end the search, if ommitted, it will find all descendants of the startingNode.
 * @returns An array of objects of all the nodes found by the search, including their depth into the tree.
 * \\{depth: number, node: LexicalNode\\} It will always return at least 1 node (the ending node) so long as it exists
 */
function $dfs(startingNode, endingNode) {
  const nodes = [];
  const start = (startingNode || lexical.$getRoot()).getLatest();
  const end = endingNode || (lexical.$isElementNode(start) ? start.getLastDescendant() || start : start);
  let node = start;
  let depth = $getDepth(node);
  while (node !== null && !node.is(end)) {
    nodes.push({
      depth,
      node
    });
    if (lexical.$isElementNode(node) && node.getChildrenSize() > 0) {
      node = node.getFirstChild();
      depth++;
    } else {
      // Find immediate sibling or nearest parent sibling
      let sibling = null;
      while (sibling === null && node !== null) {
        sibling = node.getNextSibling();
        if (sibling === null) {
          node = node.getParent();
          depth--;
        } else {
          node = sibling;
        }
      }
    }
  }
  if (node !== null && node.is(end)) {
    nodes.push({
      depth,
      node
    });
  }
  return nodes;
}
function $getDepth(node) {
  let innerNode = node;
  let depth = 0;
  while ((innerNode = innerNode.getParent()) !== null) {
    depth++;
  }
  return depth;
}

/**
 * Performs a right-to-left preorder tree traversal.
 * From the starting node it goes to the rightmost child, than backtracks to paret and finds new rightmost path.
 * It will return the next node in traversal sequence after the startingNode.
 * The traversal is similar to $dfs functions above, but the nodes are visited right-to-left, not left-to-right.
 * @param startingNode - The node to start the search.
 * @returns The next node in pre-order right to left traversal sequence or `null`, if the node does not exist
 */
function $getNextRightPreorderNode(startingNode) {
  let node = startingNode;
  if (lexical.$isElementNode(node) && node.getChildrenSize() > 0) {
    node = node.getLastChild();
  } else {
    let sibling = null;
    while (sibling === null && node !== null) {
      sibling = node.getPreviousSibling();
      if (sibling === null) {
        node = node.getParent();
      } else {
        node = sibling;
      }
    }
  }
  return node;
}

/**
 * Takes a node and traverses up its ancestors (toward the root node)
 * in order to find a specific type of node.
 * @param node - the node to begin searching.
 * @param klass - an instance of the type of node to look for.
 * @returns the node of type klass that was passed, or null if none exist.
 */
function $getNearestNodeOfType(node, klass) {
  let parent = node;
  while (parent != null) {
    if (parent instanceof klass) {
      return parent;
    }
    parent = parent.getParent();
  }
  return null;
}

/**
 * Returns the element node of the nearest ancestor, otherwise throws an error.
 * @param startNode - The starting node of the search
 * @returns The ancestor node found
 */
function $getNearestBlockElementAncestorOrThrow(startNode) {
  const blockNode = $findMatchingParent(startNode, node => lexical.$isElementNode(node) && !node.isInline());
  if (!lexical.$isElementNode(blockNode)) {
    {
      throw Error(`Expected node ${startNode.__key} to have closest block element node.`);
    }
  }
  return blockNode;
}
/**
 * Starts with a node and moves up the tree (toward the root node) to find a matching node based on
 * the search parameters of the findFn. (Consider JavaScripts' .find() function where a testing function must be
 * passed as an argument. eg. if( (node) => node.__type === 'div') ) return true; otherwise return false
 * @param startingNode - The node where the search starts.
 * @param findFn - A testing function that returns true if the current node satisfies the testing parameters.
 * @returns A parent node that matches the findFn parameters, or null if one wasn't found.
 */
const $findMatchingParent = (startingNode, findFn) => {
  let curr = startingNode;
  while (curr !== lexical.$getRoot() && curr != null) {
    if (findFn(curr)) {
      return curr;
    }
    curr = curr.getParent();
  }
  return null;
};

/**
 * Attempts to resolve nested element nodes of the same type into a single node of that type.
 * It is generally used for marks/commenting
 * @param editor - The lexical editor
 * @param targetNode - The target for the nested element to be extracted from.
 * @param cloneNode - See {@link $createMarkNode}
 * @param handleOverlap - Handles any overlap between the node to extract and the targetNode
 * @returns The lexical editor
 */
function registerNestedElementResolver(editor, targetNode, cloneNode, handleOverlap) {
  const $isTargetNode = node => {
    return node instanceof targetNode;
  };
  const $findMatch = node => {
    // First validate we don't have any children that are of the target,
    // as we need to handle them first.
    const children = node.getChildren();
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      if ($isTargetNode(child)) {
        return null;
      }
    }
    let parentNode = node;
    let childNode = node;
    while (parentNode !== null) {
      childNode = parentNode;
      parentNode = parentNode.getParent();
      if ($isTargetNode(parentNode)) {
        return {
          child: childNode,
          parent: parentNode
        };
      }
    }
    return null;
  };
  const $elementNodeTransform = node => {
    const match = $findMatch(node);
    if (match !== null) {
      const {
        child,
        parent
      } = match;

      // Simple path, we can move child out and siblings into a new parent.

      if (child.is(node)) {
        handleOverlap(parent, node);
        const nextSiblings = child.getNextSiblings();
        const nextSiblingsLength = nextSiblings.length;
        parent.insertAfter(child);
        if (nextSiblingsLength !== 0) {
          const newParent = cloneNode(parent);
          child.insertAfter(newParent);
          for (let i = 0; i < nextSiblingsLength; i++) {
            newParent.append(nextSiblings[i]);
          }
        }
        if (!parent.canBeEmpty() && parent.getChildrenSize() === 0) {
          parent.remove();
        }
      }
    }
  };
  return editor.registerNodeTransform(targetNode, $elementNodeTransform);
}

/**
 * Clones the editor and marks it as dirty to be reconciled. If there was a selection,
 * it would be set back to its previous state, or null otherwise.
 * @param editor - The lexical editor
 * @param editorState - The editor's state
 */
function $restoreEditorState(editor, editorState) {
  const FULL_RECONCILE = 2;
  const nodeMap = new Map();
  const activeEditorState = editor._pendingEditorState;
  for (const [key, node] of editorState._nodeMap) {
    nodeMap.set(key, lexical.$cloneWithProperties(node));
  }
  if (activeEditorState) {
    activeEditorState._nodeMap = nodeMap;
  }
  editor._dirtyType = FULL_RECONCILE;
  const selection = editorState._selection;
  lexical.$setSelection(selection === null ? null : selection.clone());
}

/**
 * If the selected insertion area is the root/shadow root node (see {@link lexical!$isRootOrShadowRoot}),
 * the node will be appended there, otherwise, it will be inserted before the insertion area.
 * If there is no selection where the node is to be inserted, it will be appended after any current nodes
 * within the tree, as a child of the root node. A paragraph node will then be added after the inserted node and selected.
 * @param node - The node to be inserted
 * @returns The node after its insertion
 */
function $insertNodeToNearestRoot(node) {
  const selection = lexical.$getSelection() || lexical.$getPreviousSelection();
  if (lexical.$isRangeSelection(selection)) {
    const {
      focus
    } = selection;
    const focusNode = focus.getNode();
    const focusOffset = focus.offset;
    if (lexical.$isRootOrShadowRoot(focusNode)) {
      const focusChild = focusNode.getChildAtIndex(focusOffset);
      if (focusChild == null) {
        focusNode.append(node);
      } else {
        focusChild.insertBefore(node);
      }
      node.selectNext();
    } else {
      let splitNode;
      let splitOffset;
      if (lexical.$isTextNode(focusNode)) {
        splitNode = focusNode.getParentOrThrow();
        splitOffset = focusNode.getIndexWithinParent();
        if (focusOffset > 0) {
          splitOffset += 1;
          focusNode.splitText(focusOffset);
        }
      } else {
        splitNode = focusNode;
        splitOffset = focusOffset;
      }
      const [, rightTree] = lexical.$splitNode(splitNode, splitOffset);
      rightTree.insertBefore(node);
      rightTree.selectStart();
    }
  } else {
    if (selection != null) {
      const nodes = selection.getNodes();
      nodes[nodes.length - 1].getTopLevelElementOrThrow().insertAfter(node);
    } else {
      const root = lexical.$getRoot();
      root.append(node);
    }
    const paragraphNode = lexical.$createParagraphNode();
    node.insertAfter(paragraphNode);
    paragraphNode.select();
  }
  return node.getLatest();
}

/**
 * Wraps the node into another node created from a createElementNode function, eg. $createParagraphNode
 * @param node - Node to be wrapped.
 * @param createElementNode - Creates a new lexical element to wrap the to-be-wrapped node and returns it.
 * @returns A new lexical element with the previous node appended within (as a child, including its children).
 */
function $wrapNodeInElement(node, createElementNode) {
  const elementNode = createElementNode();
  node.replace(elementNode);
  elementNode.append(node);
  return elementNode;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any

/**
 * @param object = The instance of the type
 * @param objectClass = The class of the type
 * @returns Whether the object is has the same Klass of the objectClass, ignoring the difference across window (e.g. different iframs)
 */
function objectKlassEquals(object, objectClass) {
  return object !== null ? Object.getPrototypeOf(object).constructor.name === objectClass.name : false;
}

/**
 * Filter the nodes
 * @param nodes Array of nodes that needs to be filtered
 * @param filterFn A filter function that returns node if the current node satisfies the condition otherwise null
 * @returns Array of filtered nodes
 */

function $filter(nodes, filterFn) {
  const result = [];
  for (let i = 0; i < nodes.length; i++) {
    const node = filterFn(nodes[i]);
    if (node !== null) {
      result.push(node);
    }
  }
  return result;
}
/**
 * Appends the node before the first child of the parent node
 * @param parent A parent node
 * @param node Node that needs to be appended
 */
function $insertFirst(parent, node) {
  const firstChild = parent.getFirstChild();
  if (firstChild !== null) {
    firstChild.insertBefore(node);
  } else {
    parent.append(node);
  }
}

/**
 * Calculates the zoom level of an element as a result of using
 * css zoom property.
 * @param element
 */
function calculateZoomLevel(element) {
  if (IS_FIREFOX) {
    return 1;
  }
  let zoom = 1;
  while (element) {
    zoom *= Number(window.getComputedStyle(element).getPropertyValue('zoom'));
    element = element.parentElement;
  }
  return zoom;
}

/**
 * Checks if the editor is a nested editor created by LexicalNestedComposer
 */
function $isEditorIsNestedEditor(editor) {
  return editor._parentEditor !== null;
}

exports.$splitNode = lexical.$splitNode;
exports.isBlockDomNode = lexical.isBlockDomNode;
exports.isHTMLAnchorElement = lexical.isHTMLAnchorElement;
exports.isHTMLElement = lexical.isHTMLElement;
exports.isInlineDomNode = lexical.isInlineDomNode;
exports.$dfs = $dfs;
exports.$filter = $filter;
exports.$findMatchingParent = $findMatchingParent;
exports.$getNearestBlockElementAncestorOrThrow = $getNearestBlockElementAncestorOrThrow;
exports.$getNearestNodeOfType = $getNearestNodeOfType;
exports.$getNextRightPreorderNode = $getNextRightPreorderNode;
exports.$insertFirst = $insertFirst;
exports.$insertNodeToNearestRoot = $insertNodeToNearestRoot;
exports.$isEditorIsNestedEditor = $isEditorIsNestedEditor;
exports.$restoreEditorState = $restoreEditorState;
exports.$wrapNodeInElement = $wrapNodeInElement;
exports.CAN_USE_BEFORE_INPUT = CAN_USE_BEFORE_INPUT;
exports.CAN_USE_DOM = CAN_USE_DOM;
exports.IS_ANDROID = IS_ANDROID;
exports.IS_ANDROID_CHROME = IS_ANDROID_CHROME;
exports.IS_APPLE = IS_APPLE;
exports.IS_APPLE_WEBKIT = IS_APPLE_WEBKIT;
exports.IS_CHROME = IS_CHROME;
exports.IS_FIREFOX = IS_FIREFOX;
exports.IS_IOS = IS_IOS;
exports.IS_SAFARI = IS_SAFARI;
exports.addClassNamesToElement = addClassNamesToElement;
exports.calculateZoomLevel = calculateZoomLevel;
exports.isMimeType = isMimeType;
exports.markSelection = markSelection;
exports.mediaFileReader = mediaFileReader;
exports.mergeRegister = mergeRegister;
exports.objectKlassEquals = objectKlassEquals;
exports.positionNodeOnRange = positionNodeOnRange;
exports.registerNestedElementResolver = registerNestedElementResolver;
exports.removeClassNamesFromElement = removeClassNamesFromElement;
