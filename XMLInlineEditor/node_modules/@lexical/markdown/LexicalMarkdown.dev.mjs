/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import { $isParagraphNode, $isTextNode, $getRoot, $isElementNode, $isDecoratorNode, $isLineBreakNode, $getSelection, $createTextNode, $createParagraphNode, $createLineBreakNode, $isRangeSelection, $isRootOrShadowRoot, $createRangeSelection, $setSelection } from 'lexical';
import { $createCodeNode, $isCodeNode, CodeNode } from '@lexical/code';
import { $isListNode, $isListItemNode, ListNode, ListItemNode, $createListItemNode, $createListNode } from '@lexical/list';
import { $isQuoteNode, HeadingNode, $isHeadingNode, QuoteNode, $createQuoteNode, $createHeadingNode } from '@lexical/rich-text';
import { $findMatchingParent } from '@lexical/utils';
import { LinkNode, $isLinkNode, $createLinkNode } from '@lexical/link';

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function indexBy(list, callback) {
  const index = {};
  for (const item of list) {
    const key = callback(item);
    if (index[key]) {
      index[key].push(item);
    } else {
      index[key] = [item];
    }
  }
  return index;
}
function transformersByType(transformers) {
  const byType = indexBy(transformers, t => t.type);
  return {
    element: byType.element || [],
    textFormat: byType['text-format'] || [],
    textMatch: byType['text-match'] || []
  };
}
const PUNCTUATION_OR_SPACE = /[!-/:-@[-`{-~\s]/;
const MARKDOWN_EMPTY_LINE_REG_EXP = /^\s{0,3}$/;
function isEmptyParagraph(node) {
  if (!$isParagraphNode(node)) {
    return false;
  }
  const firstChild = node.getFirstChild();
  return firstChild == null || node.getChildrenSize() === 1 && $isTextNode(firstChild) && MARKDOWN_EMPTY_LINE_REG_EXP.test(firstChild.getTextContent());
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */


/**
 * Renders string from markdown. The selection is moved to the start after the operation.
 */
function createMarkdownExport(transformers, shouldPreserveNewLines = false) {
  const byType = transformersByType(transformers);
  const isNewlineDelimited = !shouldPreserveNewLines;

  // Export only uses text formats that are responsible for single format
  // e.g. it will filter out *** (bold, italic) and instead use separate ** and *
  const textFormatTransformers = byType.textFormat.filter(transformer => transformer.format.length === 1);
  return node => {
    const output = [];
    const children = (node || $getRoot()).getChildren();
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      const result = exportTopLevelElements(child, byType.element, textFormatTransformers, byType.textMatch);
      if (result != null) {
        output.push(
        // seperate consecutive group of texts with a line break: eg. ["hello", "world"] -> ["hello", "/nworld"]
        isNewlineDelimited && i > 0 && !isEmptyParagraph(child) && !isEmptyParagraph(children[i - 1]) ? '\n'.concat(result) : result);
      }
    }
    // Ensure consecutive groups of texts are atleast \n\n apart while each empty paragraph render as a newline.
    // Eg. ["hello", "", "", "hi", "\nworld"] -> "hello\n\n\nhi\n\nworld"
    return output.join('\n');
  };
}
function exportTopLevelElements(node, elementTransformers, textTransformersIndex, textMatchTransformers) {
  for (const transformer of elementTransformers) {
    const result = transformer.export(node, _node => exportChildren(_node, textTransformersIndex, textMatchTransformers));
    if (result != null) {
      return result;
    }
  }
  if ($isElementNode(node)) {
    return exportChildren(node, textTransformersIndex, textMatchTransformers);
  } else if ($isDecoratorNode(node)) {
    return node.getTextContent();
  } else {
    return null;
  }
}
function exportChildren(node, textTransformersIndex, textMatchTransformers) {
  const output = [];
  const children = node.getChildren();
  mainLoop: for (const child of children) {
    for (const transformer of textMatchTransformers) {
      const result = transformer.export(child, parentNode => exportChildren(parentNode, textTransformersIndex, textMatchTransformers), (textNode, textContent) => exportTextFormat(textNode, textContent, textTransformersIndex));
      if (result != null) {
        output.push(result);
        continue mainLoop;
      }
    }
    if ($isLineBreakNode(child)) {
      output.push('\n');
    } else if ($isTextNode(child)) {
      output.push(exportTextFormat(child, child.getTextContent(), textTransformersIndex));
    } else if ($isElementNode(child)) {
      // empty paragraph returns ""
      output.push(exportChildren(child, textTransformersIndex, textMatchTransformers));
    } else if ($isDecoratorNode(child)) {
      output.push(child.getTextContent());
    }
  }
  return output.join('');
}
function exportTextFormat(node, textContent, textTransformers) {
  // This function handles the case of a string looking like this: "   foo   "
  // Where it would be invalid markdown to generate: "**   foo   **"
  // We instead want to trim the whitespace out, apply formatting, and then
  // bring the whitespace back. So our returned string looks like this: "   **foo**   "
  const frozenString = textContent.trim();
  let output = frozenString;
  const applied = new Set();
  for (const transformer of textTransformers) {
    const format = transformer.format[0];
    const tag = transformer.tag;
    if (hasFormat(node, format) && !applied.has(format)) {
      // Multiple tags might be used for the same format (*, _)
      applied.add(format);
      // Prevent adding opening tag is already opened by the previous sibling
      const previousNode = getTextSibling(node, true);
      if (!hasFormat(previousNode, format)) {
        output = tag + output;
      }

      // Prevent adding closing tag if next sibling will do it
      const nextNode = getTextSibling(node, false);
      if (!hasFormat(nextNode, format)) {
        output += tag;
      }
    }
  }

  // Replace trimmed version of textContent ensuring surrounding whitespace is not modified
  return textContent.replace(frozenString, () => output);
}

// Get next or previous text sibling a text node, including cases
// when it's a child of inline element (e.g. link)
function getTextSibling(node, backward) {
  let sibling = backward ? node.getPreviousSibling() : node.getNextSibling();
  if (!sibling) {
    const parent = node.getParentOrThrow();
    if (parent.isInline()) {
      sibling = backward ? parent.getPreviousSibling() : parent.getNextSibling();
    }
  }
  while (sibling) {
    if ($isElementNode(sibling)) {
      if (!sibling.isInline()) {
        break;
      }
      const descendant = backward ? sibling.getLastDescendant() : sibling.getFirstDescendant();
      if ($isTextNode(descendant)) {
        return descendant;
      } else {
        sibling = backward ? sibling.getPreviousSibling() : sibling.getNextSibling();
      }
    }
    if ($isTextNode(sibling)) {
      return sibling;
    }
    if (!$isElementNode(sibling)) {
      return null;
    }
  }
  return null;
}
function hasFormat(node, format) {
  return $isTextNode(node) && node.hasFormat(format);
}

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

const documentMode = CAN_USE_DOM && 'documentMode' in document ? document.documentMode : null;
CAN_USE_DOM && 'InputEvent' in window && !documentMode ? 'getTargetRanges' in new window.InputEvent('input') : false;
const IS_SAFARI = CAN_USE_DOM && /Version\/[\d.]+.*Safari/.test(navigator.userAgent);
const IS_IOS = CAN_USE_DOM && /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

// Keep these in case we need to use them in the future.
// export const IS_WINDOWS: boolean = CAN_USE_DOM && /Win/.test(navigator.platform);
const IS_CHROME = CAN_USE_DOM && /^(?=.*Chrome).*/i.test(navigator.userAgent);
const IS_APPLE_WEBKIT = CAN_USE_DOM && /AppleWebKit\/[\d.]+/.test(navigator.userAgent) && !IS_CHROME;

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const CODE_BLOCK_REG_EXP = /^[ \t]*```(\w{1,10})?\s?$/;
/**
 * Renders markdown from a string. The selection is moved to the start after the operation.
 */
function createMarkdownImport(transformers, shouldPreserveNewLines = false) {
  const byType = transformersByType(transformers);
  const textFormatTransformersIndex = createTextFormatTransformersIndex(byType.textFormat);
  return (markdownString, node) => {
    const lines = markdownString.split('\n');
    const linesLength = lines.length;
    const root = node || $getRoot();
    root.clear();
    for (let i = 0; i < linesLength; i++) {
      const lineText = lines[i];
      // Codeblocks are processed first as anything inside such block
      // is ignored for further processing
      // TODO:
      // Abstract it to be dynamic as other transformers (add multiline match option)
      const [codeBlockNode, shiftedIndex] = $importCodeBlock(lines, i, root);
      if (codeBlockNode != null) {
        i = shiftedIndex;
        continue;
      }
      $importBlocks(lineText, root, byType.element, textFormatTransformersIndex, byType.textMatch);
    }

    // By default, removing empty paragraphs as md does not really
    // allow empty lines and uses them as delimiter.
    // If you need empty lines set shouldPreserveNewLines = true.
    const children = root.getChildren();
    for (const child of children) {
      if (!shouldPreserveNewLines && isEmptyParagraph(child) && root.getChildrenSize() > 1) {
        child.remove();
      }
    }
    if ($getSelection() !== null) {
      root.selectStart();
    }
  };
}
function $importBlocks(lineText, rootNode, elementTransformers, textFormatTransformersIndex, textMatchTransformers) {
  const textNode = $createTextNode(lineText);
  const elementNode = $createParagraphNode();
  elementNode.append(textNode);
  rootNode.append(elementNode);
  for (const {
    regExp,
    replace
  } of elementTransformers) {
    const match = lineText.match(regExp);
    if (match) {
      textNode.setTextContent(lineText.slice(match[0].length));
      replace(elementNode, [textNode], match, true);
      break;
    }
  }
  importTextFormatTransformers(textNode, textFormatTransformersIndex, textMatchTransformers);

  // If no transformer found and we left with original paragraph node
  // can check if its content can be appended to the previous node
  // if it's a paragraph, quote or list
  if (elementNode.isAttached() && lineText.length > 0) {
    const previousNode = elementNode.getPreviousSibling();
    if ($isParagraphNode(previousNode) || $isQuoteNode(previousNode) || $isListNode(previousNode)) {
      let targetNode = previousNode;
      if ($isListNode(previousNode)) {
        const lastDescendant = previousNode.getLastDescendant();
        if (lastDescendant == null) {
          targetNode = null;
        } else {
          targetNode = $findMatchingParent(lastDescendant, $isListItemNode);
        }
      }
      if (targetNode != null && targetNode.getTextContentSize() > 0) {
        targetNode.splice(targetNode.getChildrenSize(), 0, [$createLineBreakNode(), ...elementNode.getChildren()]);
        elementNode.remove();
      }
    }
  }
}
function $importCodeBlock(lines, startLineIndex, rootNode) {
  const openMatch = lines[startLineIndex].match(CODE_BLOCK_REG_EXP);
  if (openMatch) {
    let endLineIndex = startLineIndex;
    const linesLength = lines.length;
    while (++endLineIndex < linesLength) {
      const closeMatch = lines[endLineIndex].match(CODE_BLOCK_REG_EXP);
      if (closeMatch) {
        const codeBlockNode = $createCodeNode(openMatch[1]);
        const textNode = $createTextNode(lines.slice(startLineIndex + 1, endLineIndex).join('\n'));
        codeBlockNode.append(textNode);
        rootNode.append(codeBlockNode);
        return [codeBlockNode, endLineIndex];
      }
    }
  }
  return [null, startLineIndex];
}

// Processing text content and replaces text format tags.
// It takes outermost tag match and its content, creates text node with
// format based on tag and then recursively executed over node's content
//
// E.g. for "*Hello **world**!*" string it will create text node with
// "Hello **world**!" content and italic format and run recursively over
// its content to transform "**world**" part
function importTextFormatTransformers(textNode, textFormatTransformersIndex, textMatchTransformers) {
  const textContent = textNode.getTextContent();
  const match = findOutermostMatch(textContent, textFormatTransformersIndex);
  if (!match) {
    // Once text format processing is done run text match transformers, as it
    // only can span within single text node (unline formats that can cover multiple nodes)
    importTextMatchTransformers(textNode, textMatchTransformers);
    return;
  }
  let currentNode, remainderNode, leadingNode;

  // If matching full content there's no need to run splitText and can reuse existing textNode
  // to update its content and apply format. E.g. for **_Hello_** string after applying bold
  // format (**) it will reuse the same text node to apply italic (_)
  if (match[0] === textContent) {
    currentNode = textNode;
  } else {
    const startIndex = match.index || 0;
    const endIndex = startIndex + match[0].length;
    if (startIndex === 0) {
      [currentNode, remainderNode] = textNode.splitText(endIndex);
    } else {
      [leadingNode, currentNode, remainderNode] = textNode.splitText(startIndex, endIndex);
    }
  }
  currentNode.setTextContent(match[2]);
  const transformer = textFormatTransformersIndex.transformersByTag[match[1]];
  if (transformer) {
    for (const format of transformer.format) {
      if (!currentNode.hasFormat(format)) {
        currentNode.toggleFormat(format);
      }
    }
  }

  // Recursively run over inner text if it's not inline code
  if (!currentNode.hasFormat('code')) {
    importTextFormatTransformers(currentNode, textFormatTransformersIndex, textMatchTransformers);
  }

  // Run over leading/remaining text if any
  if (leadingNode) {
    importTextFormatTransformers(leadingNode, textFormatTransformersIndex, textMatchTransformers);
  }
  if (remainderNode) {
    importTextFormatTransformers(remainderNode, textFormatTransformersIndex, textMatchTransformers);
  }
}
function importTextMatchTransformers(textNode_, textMatchTransformers) {
  let textNode = textNode_;
  mainLoop: while (textNode) {
    for (const transformer of textMatchTransformers) {
      const match = textNode.getTextContent().match(transformer.importRegExp);
      if (!match) {
        continue;
      }
      const startIndex = match.index || 0;
      const endIndex = startIndex + match[0].length;
      let replaceNode, newTextNode;
      if (startIndex === 0) {
        [replaceNode, textNode] = textNode.splitText(endIndex);
      } else {
        [, replaceNode, newTextNode] = textNode.splitText(startIndex, endIndex);
      }
      if (newTextNode) {
        importTextMatchTransformers(newTextNode, textMatchTransformers);
      }
      transformer.replace(replaceNode, match);
      continue mainLoop;
    }
    break;
  }
}

// Finds first "<tag>content<tag>" match that is not nested into another tag
function findOutermostMatch(textContent, textTransformersIndex) {
  const openTagsMatch = textContent.match(textTransformersIndex.openTagsRegExp);
  if (openTagsMatch == null) {
    return null;
  }
  for (const match of openTagsMatch) {
    // Open tags reg exp might capture leading space so removing it
    // before using match to find transformer
    const tag = match.replace(/^\s/, '');
    const fullMatchRegExp = textTransformersIndex.fullMatchRegExpByTag[tag];
    if (fullMatchRegExp == null) {
      continue;
    }
    const fullMatch = textContent.match(fullMatchRegExp);
    const transformer = textTransformersIndex.transformersByTag[tag];
    if (fullMatch != null && transformer != null) {
      if (transformer.intraword !== false) {
        return fullMatch;
      }

      // For non-intraword transformers checking if it's within a word
      // or surrounded with space/punctuation/newline
      const {
        index = 0
      } = fullMatch;
      const beforeChar = textContent[index - 1];
      const afterChar = textContent[index + fullMatch[0].length];
      if ((!beforeChar || PUNCTUATION_OR_SPACE.test(beforeChar)) && (!afterChar || PUNCTUATION_OR_SPACE.test(afterChar))) {
        return fullMatch;
      }
    }
  }
  return null;
}
function createTextFormatTransformersIndex(textTransformers) {
  const transformersByTag = {};
  const fullMatchRegExpByTag = {};
  const openTagsRegExp = [];
  const escapeRegExp = `(?<![\\\\])`;
  for (const transformer of textTransformers) {
    const {
      tag
    } = transformer;
    transformersByTag[tag] = transformer;
    const tagRegExp = tag.replace(/(\*|\^|\+)/g, '\\$1');
    openTagsRegExp.push(tagRegExp);
    if (IS_SAFARI || IS_IOS || IS_APPLE_WEBKIT) {
      fullMatchRegExpByTag[tag] = new RegExp(`(${tagRegExp})(?![${tagRegExp}\\s])(.*?[^${tagRegExp}\\s])${tagRegExp}(?!${tagRegExp})`);
    } else {
      fullMatchRegExpByTag[tag] = new RegExp(`(?<![\\\\${tagRegExp}])(${tagRegExp})((\\\\${tagRegExp})?.*?[^${tagRegExp}\\s](\\\\${tagRegExp})?)((?<!\\\\)|(?<=\\\\\\\\))(${tagRegExp})(?![\\\\${tagRegExp}])`);
    }
  }
  return {
    // Reg exp to find open tag + content + close tag
    fullMatchRegExpByTag,
    // Reg exp to find opening tags
    openTagsRegExp: new RegExp((IS_SAFARI || IS_IOS || IS_APPLE_WEBKIT ? '' : `${escapeRegExp}`) + '(' + openTagsRegExp.join('|') + ')', 'g'),
    transformersByTag
  };
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function runElementTransformers(parentNode, anchorNode, anchorOffset, elementTransformers) {
  const grandParentNode = parentNode.getParent();
  if (!$isRootOrShadowRoot(grandParentNode) || parentNode.getFirstChild() !== anchorNode) {
    return false;
  }
  const textContent = anchorNode.getTextContent();

  // Checking for anchorOffset position to prevent any checks for cases when caret is too far
  // from a line start to be a part of block-level markdown trigger.
  //
  // TODO:
  // Can have a quick check if caret is close enough to the beginning of the string (e.g. offset less than 10-20)
  // since otherwise it won't be a markdown shortcut, but tables are exception
  if (textContent[anchorOffset - 1] !== ' ') {
    return false;
  }
  for (const {
    regExp,
    replace
  } of elementTransformers) {
    const match = textContent.match(regExp);
    if (match && match[0].length === anchorOffset) {
      const nextSiblings = anchorNode.getNextSiblings();
      const [leadingNode, remainderNode] = anchorNode.splitText(anchorOffset);
      leadingNode.remove();
      const siblings = remainderNode ? [remainderNode, ...nextSiblings] : nextSiblings;
      replace(parentNode, siblings, match, false);
      return true;
    }
  }
  return false;
}
function runTextMatchTransformers(anchorNode, anchorOffset, transformersByTrigger) {
  let textContent = anchorNode.getTextContent();
  const lastChar = textContent[anchorOffset - 1];
  const transformers = transformersByTrigger[lastChar];
  if (transformers == null) {
    return false;
  }

  // If typing in the middle of content, remove the tail to do
  // reg exp match up to a string end (caret position)
  if (anchorOffset < textContent.length) {
    textContent = textContent.slice(0, anchorOffset);
  }
  for (const transformer of transformers) {
    const match = textContent.match(transformer.regExp);
    if (match === null) {
      continue;
    }
    const startIndex = match.index || 0;
    const endIndex = startIndex + match[0].length;
    let replaceNode;
    if (startIndex === 0) {
      [replaceNode] = anchorNode.splitText(endIndex);
    } else {
      [, replaceNode] = anchorNode.splitText(startIndex, endIndex);
    }
    replaceNode.selectNext(0, 0);
    transformer.replace(replaceNode, match);
    return true;
  }
  return false;
}
function $runTextFormatTransformers(anchorNode, anchorOffset, textFormatTransformers) {
  const textContent = anchorNode.getTextContent();
  const closeTagEndIndex = anchorOffset - 1;
  const closeChar = textContent[closeTagEndIndex];
  // Quick check if we're possibly at the end of inline markdown style
  const matchers = textFormatTransformers[closeChar];
  if (!matchers) {
    return false;
  }
  for (const matcher of matchers) {
    const {
      tag
    } = matcher;
    const tagLength = tag.length;
    const closeTagStartIndex = closeTagEndIndex - tagLength + 1;

    // If tag is not single char check if rest of it matches with text content
    if (tagLength > 1) {
      if (!isEqualSubString(textContent, closeTagStartIndex, tag, 0, tagLength)) {
        continue;
      }
    }

    // Space before closing tag cancels inline markdown
    if (textContent[closeTagStartIndex - 1] === ' ') {
      continue;
    }

    // Some tags can not be used within words, hence should have newline/space/punctuation after it
    const afterCloseTagChar = textContent[closeTagEndIndex + 1];
    if (matcher.intraword === false && afterCloseTagChar && !PUNCTUATION_OR_SPACE.test(afterCloseTagChar)) {
      continue;
    }
    const closeNode = anchorNode;
    let openNode = closeNode;
    let openTagStartIndex = getOpenTagStartIndex(textContent, closeTagStartIndex, tag);

    // Go through text node siblings and search for opening tag
    // if haven't found it within the same text node as closing tag
    let sibling = openNode;
    while (openTagStartIndex < 0 && (sibling = sibling.getPreviousSibling())) {
      if ($isLineBreakNode(sibling)) {
        break;
      }
      if ($isTextNode(sibling)) {
        const siblingTextContent = sibling.getTextContent();
        openNode = sibling;
        openTagStartIndex = getOpenTagStartIndex(siblingTextContent, siblingTextContent.length, tag);
      }
    }

    // Opening tag is not found
    if (openTagStartIndex < 0) {
      continue;
    }

    // No content between opening and closing tag
    if (openNode === closeNode && openTagStartIndex + tagLength === closeTagStartIndex) {
      continue;
    }

    // Checking longer tags for repeating chars (e.g. *** vs **)
    const prevOpenNodeText = openNode.getTextContent();
    if (openTagStartIndex > 0 && prevOpenNodeText[openTagStartIndex - 1] === closeChar) {
      continue;
    }

    // Some tags can not be used within words, hence should have newline/space/punctuation before it
    const beforeOpenTagChar = prevOpenNodeText[openTagStartIndex - 1];
    if (matcher.intraword === false && beforeOpenTagChar && !PUNCTUATION_OR_SPACE.test(beforeOpenTagChar)) {
      continue;
    }

    // Clean text from opening and closing tags (starting from closing tag
    // to prevent any offset shifts if we start from opening one)
    const prevCloseNodeText = closeNode.getTextContent();
    const closeNodeText = prevCloseNodeText.slice(0, closeTagStartIndex) + prevCloseNodeText.slice(closeTagEndIndex + 1);
    closeNode.setTextContent(closeNodeText);
    const openNodeText = openNode === closeNode ? closeNodeText : prevOpenNodeText;
    openNode.setTextContent(openNodeText.slice(0, openTagStartIndex) + openNodeText.slice(openTagStartIndex + tagLength));
    const selection = $getSelection();
    const nextSelection = $createRangeSelection();
    $setSelection(nextSelection);
    // Adjust offset based on deleted chars
    const newOffset = closeTagEndIndex - tagLength * (openNode === closeNode ? 2 : 1) + 1;
    nextSelection.anchor.set(openNode.__key, openTagStartIndex, 'text');
    nextSelection.focus.set(closeNode.__key, newOffset, 'text');

    // Apply formatting to selected text
    for (const format of matcher.format) {
      if (!nextSelection.hasFormat(format)) {
        nextSelection.formatText(format);
      }
    }

    // Collapse selection up to the focus point
    nextSelection.anchor.set(nextSelection.focus.key, nextSelection.focus.offset, nextSelection.focus.type);

    // Remove formatting from collapsed selection
    for (const format of matcher.format) {
      if (nextSelection.hasFormat(format)) {
        nextSelection.toggleFormat(format);
      }
    }
    if ($isRangeSelection(selection)) {
      nextSelection.format = selection.format;
    }
    return true;
  }
  return false;
}
function getOpenTagStartIndex(string, maxIndex, tag) {
  const tagLength = tag.length;
  for (let i = maxIndex; i >= tagLength; i--) {
    const startIndex = i - tagLength;
    if (isEqualSubString(string, startIndex, tag, 0, tagLength) &&
    // Space after opening tag cancels transformation
    string[startIndex + tagLength] !== ' ') {
      return startIndex;
    }
  }
  return -1;
}
function isEqualSubString(stringA, aStart, stringB, bStart, length) {
  for (let i = 0; i < length; i++) {
    if (stringA[aStart + i] !== stringB[bStart + i]) {
      return false;
    }
  }
  return true;
}
function registerMarkdownShortcuts(editor, transformers = TRANSFORMERS) {
  const byType = transformersByType(transformers);
  const textFormatTransformersIndex = indexBy(byType.textFormat, ({
    tag
  }) => tag[tag.length - 1]);
  const textMatchTransformersIndex = indexBy(byType.textMatch, ({
    trigger
  }) => trigger);
  for (const transformer of transformers) {
    const type = transformer.type;
    if (type === 'element' || type === 'text-match') {
      const dependencies = transformer.dependencies;
      for (const node of dependencies) {
        if (!editor.hasNode(node)) {
          {
            throw Error(`MarkdownShortcuts: missing dependency ${node.getType()} for transformer. Ensure node dependency is included in editor initial config.`);
          }
        }
      }
    }
  }
  const $transform = (parentNode, anchorNode, anchorOffset) => {
    if (runElementTransformers(parentNode, anchorNode, anchorOffset, byType.element)) {
      return;
    }
    if (runTextMatchTransformers(anchorNode, anchorOffset, textMatchTransformersIndex)) {
      return;
    }
    $runTextFormatTransformers(anchorNode, anchorOffset, textFormatTransformersIndex);
  };
  return editor.registerUpdateListener(({
    tags,
    dirtyLeaves,
    editorState,
    prevEditorState
  }) => {
    // Ignore updates from collaboration and undo/redo (as changes already calculated)
    if (tags.has('collaboration') || tags.has('historic')) {
      return;
    }

    // If editor is still composing (i.e. backticks) we must wait before the user confirms the key
    if (editor.isComposing()) {
      return;
    }
    const selection = editorState.read($getSelection);
    const prevSelection = prevEditorState.read($getSelection);
    if (!$isRangeSelection(prevSelection) || !$isRangeSelection(selection) || !selection.isCollapsed()) {
      return;
    }
    const anchorKey = selection.anchor.key;
    const anchorOffset = selection.anchor.offset;
    const anchorNode = editorState._nodeMap.get(anchorKey);
    if (!$isTextNode(anchorNode) || !dirtyLeaves.has(anchorKey) || anchorOffset !== 1 && anchorOffset > prevSelection.anchor.offset + 1) {
      return;
    }
    editor.update(() => {
      // Markdown is not available inside code
      if (anchorNode.hasFormat('code')) {
        return;
      }
      const parentNode = anchorNode.getParent();
      if (parentNode === null || $isCodeNode(parentNode)) {
        return;
      }
      $transform(parentNode, anchorNode, selection.anchor.offset);
    });
  });
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const createBlockNode = createNode => {
  return (parentNode, children, match) => {
    const node = createNode(match);
    node.append(...children);
    parentNode.replace(node);
    node.select(0, 0);
  };
};

// Amount of spaces that define indentation level
// TODO: should be an option
const LIST_INDENT_SIZE = 4;
function getIndent(whitespaces) {
  const tabs = whitespaces.match(/\t/g);
  const spaces = whitespaces.match(/ /g);
  let indent = 0;
  if (tabs) {
    indent += tabs.length;
  }
  if (spaces) {
    indent += Math.floor(spaces.length / LIST_INDENT_SIZE);
  }
  return indent;
}
const listReplace = listType => {
  return (parentNode, children, match) => {
    const previousNode = parentNode.getPreviousSibling();
    const nextNode = parentNode.getNextSibling();
    const listItem = $createListItemNode(listType === 'check' ? match[3] === 'x' : undefined);
    if ($isListNode(nextNode) && nextNode.getListType() === listType) {
      const firstChild = nextNode.getFirstChild();
      if (firstChild !== null) {
        firstChild.insertBefore(listItem);
      } else {
        // should never happen, but let's handle gracefully, just in case.
        nextNode.append(listItem);
      }
      parentNode.remove();
    } else if ($isListNode(previousNode) && previousNode.getListType() === listType) {
      previousNode.append(listItem);
      parentNode.remove();
    } else {
      const list = $createListNode(listType, listType === 'number' ? Number(match[2]) : undefined);
      list.append(listItem);
      parentNode.replace(list);
    }
    listItem.append(...children);
    listItem.select(0, 0);
    const indent = getIndent(match[1]);
    if (indent) {
      listItem.setIndent(indent);
    }
  };
};
const listExport = (listNode, exportChildren, depth) => {
  const output = [];
  const children = listNode.getChildren();
  let index = 0;
  for (const listItemNode of children) {
    if ($isListItemNode(listItemNode)) {
      if (listItemNode.getChildrenSize() === 1) {
        const firstChild = listItemNode.getFirstChild();
        if ($isListNode(firstChild)) {
          output.push(listExport(firstChild, exportChildren, depth + 1));
          continue;
        }
      }
      const indent = ' '.repeat(depth * LIST_INDENT_SIZE);
      const listType = listNode.getListType();
      const prefix = listType === 'number' ? `${listNode.getStart() + index}. ` : listType === 'check' ? `- [${listItemNode.getChecked() ? 'x' : ' '}] ` : '- ';
      output.push(indent + prefix + exportChildren(listItemNode));
      index++;
    }
  }
  return output.join('\n');
};
const HEADING = {
  dependencies: [HeadingNode],
  export: (node, exportChildren) => {
    if (!$isHeadingNode(node)) {
      return null;
    }
    const level = Number(node.getTag().slice(1));
    return '#'.repeat(level) + ' ' + exportChildren(node);
  },
  regExp: /^(#{1,6})\s/,
  replace: createBlockNode(match => {
    const tag = 'h' + match[1].length;
    return $createHeadingNode(tag);
  }),
  type: 'element'
};
const QUOTE = {
  dependencies: [QuoteNode],
  export: (node, exportChildren) => {
    if (!$isQuoteNode(node)) {
      return null;
    }
    const lines = exportChildren(node).split('\n');
    const output = [];
    for (const line of lines) {
      output.push('> ' + line);
    }
    return output.join('\n');
  },
  regExp: /^>\s/,
  replace: (parentNode, children, _match, isImport) => {
    if (isImport) {
      const previousNode = parentNode.getPreviousSibling();
      if ($isQuoteNode(previousNode)) {
        previousNode.splice(previousNode.getChildrenSize(), 0, [$createLineBreakNode(), ...children]);
        previousNode.select(0, 0);
        parentNode.remove();
        return;
      }
    }
    const node = $createQuoteNode();
    node.append(...children);
    parentNode.replace(node);
    node.select(0, 0);
  },
  type: 'element'
};
const CODE = {
  dependencies: [CodeNode],
  export: node => {
    if (!$isCodeNode(node)) {
      return null;
    }
    const textContent = node.getTextContent();
    return '```' + (node.getLanguage() || '') + (textContent ? '\n' + textContent : '') + '\n' + '```';
  },
  regExp: /^[ \t]*```(\w{1,10})?\s/,
  replace: createBlockNode(match => {
    return $createCodeNode(match ? match[1] : undefined);
  }),
  type: 'element'
};
const UNORDERED_LIST = {
  dependencies: [ListNode, ListItemNode],
  export: (node, exportChildren) => {
    return $isListNode(node) ? listExport(node, exportChildren, 0) : null;
  },
  regExp: /^(\s*)[-*+]\s/,
  replace: listReplace('bullet'),
  type: 'element'
};
const CHECK_LIST = {
  dependencies: [ListNode, ListItemNode],
  export: (node, exportChildren) => {
    return $isListNode(node) ? listExport(node, exportChildren, 0) : null;
  },
  regExp: /^(\s*)(?:-\s)?\s?(\[(\s|x)?\])\s/i,
  replace: listReplace('check'),
  type: 'element'
};
const ORDERED_LIST = {
  dependencies: [ListNode, ListItemNode],
  export: (node, exportChildren) => {
    return $isListNode(node) ? listExport(node, exportChildren, 0) : null;
  },
  regExp: /^(\s*)(\d{1,})\.\s/,
  replace: listReplace('number'),
  type: 'element'
};
const INLINE_CODE = {
  format: ['code'],
  tag: '`',
  type: 'text-format'
};
const HIGHLIGHT = {
  format: ['highlight'],
  tag: '==',
  type: 'text-format'
};
const BOLD_ITALIC_STAR = {
  format: ['bold', 'italic'],
  tag: '***',
  type: 'text-format'
};
const BOLD_ITALIC_UNDERSCORE = {
  format: ['bold', 'italic'],
  intraword: false,
  tag: '___',
  type: 'text-format'
};
const BOLD_STAR = {
  format: ['bold'],
  tag: '**',
  type: 'text-format'
};
const BOLD_UNDERSCORE = {
  format: ['bold'],
  intraword: false,
  tag: '__',
  type: 'text-format'
};
const STRIKETHROUGH = {
  format: ['strikethrough'],
  tag: '~~',
  type: 'text-format'
};
const ITALIC_STAR = {
  format: ['italic'],
  tag: '*',
  type: 'text-format'
};
const ITALIC_UNDERSCORE = {
  format: ['italic'],
  intraword: false,
  tag: '_',
  type: 'text-format'
};

// Order of text transformers matters:
//
// - code should go first as it prevents any transformations inside
// - then longer tags match (e.g. ** or __ should go before * or _)
const LINK = {
  dependencies: [LinkNode],
  export: (node, exportChildren, exportFormat) => {
    if (!$isLinkNode(node)) {
      return null;
    }
    const title = node.getTitle();
    const linkContent = title ? `[${node.getTextContent()}](${node.getURL()} "${title}")` : `[${node.getTextContent()}](${node.getURL()})`;
    const firstChild = node.getFirstChild();
    // Add text styles only if link has single text node inside. If it's more
    // then one we ignore it as markdown does not support nested styles for links
    if (node.getChildrenSize() === 1 && $isTextNode(firstChild)) {
      return exportFormat(firstChild, linkContent);
    } else {
      return linkContent;
    }
  },
  importRegExp: /(?:\[([^[]+)\])(?:\((?:([^()\s]+)(?:\s"((?:[^"]*\\")*[^"]*)"\s*)?)\))/,
  regExp: /(?:\[([^[]+)\])(?:\((?:([^()\s]+)(?:\s"((?:[^"]*\\")*[^"]*)"\s*)?)\))$/,
  replace: (textNode, match) => {
    const [, linkText, linkUrl, linkTitle] = match;
    const linkNode = $createLinkNode(linkUrl, {
      title: linkTitle
    });
    const linkTextNode = $createTextNode(linkText);
    linkTextNode.setFormat(textNode.getFormat());
    linkNode.append(linkTextNode);
    textNode.replace(linkNode);
  },
  trigger: ')',
  type: 'text-match'
};

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

const ELEMENT_TRANSFORMERS = [HEADING, QUOTE, CODE, UNORDERED_LIST, ORDERED_LIST];

// Order of text format transformers matters:
//
// - code should go first as it prevents any transformations inside
// - then longer tags match (e.g. ** or __ should go before * or _)
const TEXT_FORMAT_TRANSFORMERS = [INLINE_CODE, BOLD_ITALIC_STAR, BOLD_ITALIC_UNDERSCORE, BOLD_STAR, BOLD_UNDERSCORE, HIGHLIGHT, ITALIC_STAR, ITALIC_UNDERSCORE, STRIKETHROUGH];
const TEXT_MATCH_TRANSFORMERS = [LINK];
const TRANSFORMERS = [...ELEMENT_TRANSFORMERS, ...TEXT_FORMAT_TRANSFORMERS, ...TEXT_MATCH_TRANSFORMERS];

/**
 * Renders markdown from a string. The selection is moved to the start after the operation.
 */
function $convertFromMarkdownString(markdown, transformers = TRANSFORMERS, node, shouldPreserveNewLines = false) {
  const importMarkdown = createMarkdownImport(transformers, shouldPreserveNewLines);
  return importMarkdown(markdown, node);
}

/**
 * Renders string from markdown. The selection is moved to the start after the operation.
 */
function $convertToMarkdownString(transformers = TRANSFORMERS, node, shouldPreserveNewLines = false) {
  const exportMarkdown = createMarkdownExport(transformers, shouldPreserveNewLines);
  return exportMarkdown(node);
}

export { $convertFromMarkdownString, $convertToMarkdownString, BOLD_ITALIC_STAR, BOLD_ITALIC_UNDERSCORE, BOLD_STAR, BOLD_UNDERSCORE, CHECK_LIST, CODE, ELEMENT_TRANSFORMERS, HEADING, HIGHLIGHT, INLINE_CODE, ITALIC_STAR, ITALIC_UNDERSCORE, LINK, ORDERED_LIST, QUOTE, STRIKETHROUGH, TEXT_FORMAT_TRANSFORMERS, TEXT_MATCH_TRANSFORMERS, TRANSFORMERS, UNORDERED_LIST, registerMarkdownShortcuts };
