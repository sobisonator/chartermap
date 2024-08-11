/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import{INSERT_ORDERED_LIST_COMMAND as r,insertList as e,INSERT_UNORDERED_LIST_COMMAND as o,REMOVE_LIST_COMMAND as t,removeList as i,$handleListInsertParagraph as m,ListNode as n,ListItemNode as l}from"@lexical/list";import{useLexicalComposerContext as s}from"@lexical/react/LexicalComposerContext";import{useEffect as a}from"react";import{mergeRegister as c}from"@lexical/utils";import{COMMAND_PRIORITY_LOW as d,INSERT_PARAGRAPH_COMMAND as f}from"lexical";function u(){const[u]=s();return a((()=>{if(!u.hasNodes([n,l]))throw new Error("ListPlugin: ListNode and/or ListItemNode not registered on editor")}),[u]),function(n){a((()=>c(n.registerCommand(r,(()=>(e(n,"number"),!0)),d),n.registerCommand(o,(()=>(e(n,"bullet"),!0)),d),n.registerCommand(t,(()=>(i(n),!0)),d),n.registerCommand(f,(()=>!!m()),d))),[n])}(u),null}export{u as ListPlugin};
