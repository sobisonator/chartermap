/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';

var LexicalComposerContext = require('@lexical/react/LexicalComposerContext');
var table = require('@lexical/table');
var utils = require('@lexical/utils');
var lexical = require('lexical');
var react = require('react');

/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

function TablePlugin({
  hasCellMerge = true,
  hasCellBackgroundColor = true,
  hasTabHandler = true
}) {
  const [editor] = LexicalComposerContext.useLexicalComposerContext();
  react.useEffect(() => {
    if (!editor.hasNodes([table.TableNode, table.TableCellNode, table.TableRowNode])) {
      {
        throw Error(`TablePlugin: TableNode, TableCellNode or TableRowNode not registered on editor`);
      }
    }
    return utils.mergeRegister(editor.registerCommand(table.INSERT_TABLE_COMMAND, ({
      columns,
      rows,
      includeHeaders
    }) => {
      const tableNode = table.$createTableNodeWithDimensions(Number(rows), Number(columns), includeHeaders);
      utils.$insertNodeToNearestRoot(tableNode);
      const firstDescendant = tableNode.getFirstDescendant();
      if (lexical.$isTextNode(firstDescendant)) {
        firstDescendant.select();
      }
      return true;
    }, lexical.COMMAND_PRIORITY_EDITOR), editor.registerNodeTransform(table.TableNode, node => {
      const [gridMap] = table.$computeTableMapSkipCellCheck(node, null, null);
      const maxRowLength = gridMap.reduce((curLength, row) => {
        return Math.max(curLength, row.length);
      }, 0);
      for (let i = 0; i < gridMap.length; ++i) {
        const rowLength = gridMap[i].length;
        if (rowLength === maxRowLength) {
          continue;
        }
        const lastCellMap = gridMap[i][rowLength - 1];
        const lastRowCell = lastCellMap.cell;
        for (let j = rowLength; j < maxRowLength; ++j) {
          // TODO: inherit header state from another header or body
          const newCell = table.$createTableCellNode(0);
          newCell.append(lexical.$createParagraphNode());
          if (lastRowCell !== null) {
            lastRowCell.insertAfter(newCell);
          } else {
            utils.$insertFirst(lastRowCell, newCell);
          }
        }
      }
    }));
  }, [editor]);
  react.useEffect(() => {
    const tableSelections = new Map();
    const initializeTableNode = tableNode => {
      const nodeKey = tableNode.getKey();
      const tableElement = editor.getElementByKey(nodeKey);
      if (tableElement && !tableSelections.has(nodeKey)) {
        const tableSelection = table.applyTableHandlers(tableNode, tableElement, editor, hasTabHandler);
        tableSelections.set(nodeKey, tableSelection);
      }
    };
    const unregisterMutationListener = editor.registerMutationListener(table.TableNode, nodeMutations => {
      for (const [nodeKey, mutation] of nodeMutations) {
        if (mutation === 'created') {
          editor.getEditorState().read(() => {
            const tableNode = lexical.$getNodeByKey(nodeKey);
            if (table.$isTableNode(tableNode)) {
              initializeTableNode(tableNode);
            }
          });
        } else if (mutation === 'destroyed') {
          const tableSelection = tableSelections.get(nodeKey);
          if (tableSelection !== undefined) {
            tableSelection.removeListeners();
            tableSelections.delete(nodeKey);
          }
        }
      }
    }, {
      skipInitialization: false
    });
    return () => {
      unregisterMutationListener();
      // Hook might be called multiple times so cleaning up tables listeners as well,
      // as it'll be reinitialized during recurring call
      for (const [, tableSelection] of tableSelections) {
        tableSelection.removeListeners();
      }
    };
  }, [editor, hasTabHandler]);

  // Unmerge cells when the feature isn't enabled
  react.useEffect(() => {
    if (hasCellMerge) {
      return;
    }
    return editor.registerNodeTransform(table.TableCellNode, node => {
      if (node.getColSpan() > 1 || node.getRowSpan() > 1) {
        // When we have rowSpan we have to map the entire Table to understand where the new Cells
        // fit best; let's analyze all Cells at once to save us from further transform iterations
        const [,, gridNode] = table.$getNodeTriplet(node);
        const [gridMap] = table.$computeTableMap(gridNode, node, node);
        // TODO this function expects Tables to be normalized. Look into this once it exists
        const rowsCount = gridMap.length;
        const columnsCount = gridMap[0].length;
        let row = gridNode.getFirstChild();
        if (!table.$isTableRowNode(row)) {
          throw Error(`Expected TableNode first child to be a RowNode`);
        }
        const unmerged = [];
        for (let i = 0; i < rowsCount; i++) {
          if (i !== 0) {
            row = row.getNextSibling();
            if (!table.$isTableRowNode(row)) {
              throw Error(`Expected TableNode first child to be a RowNode`);
            }
          }
          let lastRowCell = null;
          for (let j = 0; j < columnsCount; j++) {
            const cellMap = gridMap[i][j];
            const cell = cellMap.cell;
            if (cellMap.startRow === i && cellMap.startColumn === j) {
              lastRowCell = cell;
              unmerged.push(cell);
            } else if (cell.getColSpan() > 1 || cell.getRowSpan() > 1) {
              if (!table.$isTableCellNode(cell)) {
                throw Error(`Expected TableNode cell to be a TableCellNode`);
              }
              const newCell = table.$createTableCellNode(cell.__headerState);
              if (lastRowCell !== null) {
                lastRowCell.insertAfter(newCell);
              } else {
                utils.$insertFirst(row, newCell);
              }
            }
          }
        }
        for (const cell of unmerged) {
          cell.setColSpan(1);
          cell.setRowSpan(1);
        }
      }
    });
  }, [editor, hasCellMerge]);

  // Remove cell background color when feature is disabled
  react.useEffect(() => {
    if (hasCellBackgroundColor) {
      return;
    }
    return editor.registerNodeTransform(table.TableCellNode, node => {
      if (node.getBackgroundColor() !== null) {
        node.setBackgroundColor(null);
      }
    });
  }, [editor, hasCellBackgroundColor, hasCellMerge]);
  return null;
}

exports.TablePlugin = TablePlugin;
