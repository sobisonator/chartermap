/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import { INSERT_ORDERED_LIST_COMMAND, insertList, INSERT_UNORDERED_LIST_COMMAND, REMOVE_LIST_COMMAND, removeList, $handleListInsertParagraph, ListNode, ListItemNode } from '@lexical/list';
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext';
import { useEffect } from 'react';
import { mergeRegister } from '@lexical/utils';
import { COMMAND_PRIORITY_LOW, INSERT_PARAGRAPH_COMMAND } from 'lexical';

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function useList(editor) {
  useEffect(() => {
    return mergeRegister(editor.registerCommand(INSERT_ORDERED_LIST_COMMAND, () => {
      insertList(editor, 'number');
      return true;
    }, COMMAND_PRIORITY_LOW), editor.registerCommand(INSERT_UNORDERED_LIST_COMMAND, () => {
      insertList(editor, 'bullet');
      return true;
    }, COMMAND_PRIORITY_LOW), editor.registerCommand(REMOVE_LIST_COMMAND, () => {
      removeList(editor);
      return true;
    }, COMMAND_PRIORITY_LOW), editor.registerCommand(INSERT_PARAGRAPH_COMMAND, () => {
      const hasHandledInsertParagraph = $handleListInsertParagraph();
      if (hasHandledInsertParagraph) {
        return true;
      }
      return false;
    }, COMMAND_PRIORITY_LOW));
  }, [editor]);
}

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function ListPlugin() {
  const [editor] = useLexicalComposerContext();
  useEffect(() => {
    if (!editor.hasNodes([ListNode, ListItemNode])) {
      throw new Error('ListPlugin: ListNode and/or ListItemNode not registered on editor');
    }
  }, [editor]);
  useList(editor);
  return null;
}

export { ListPlugin };
