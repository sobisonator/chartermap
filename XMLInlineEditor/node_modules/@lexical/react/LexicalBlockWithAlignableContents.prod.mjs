/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import{useLexicalComposerContext as e}from"@lexical/react/LexicalComposerContext";import{$isDecoratorBlockNode as r}from"@lexical/react/LexicalDecoratorBlockNode";import{useLexicalNodeSelection as t}from"@lexical/react/useLexicalNodeSelection";import{mergeRegister as o,$getNearestBlockElementAncestorOrThrow as i}from"@lexical/utils";import{$isNodeSelection as l,$getSelection as a,$getNodeByKey as m,$isDecoratorNode as n,FORMAT_ELEMENT_COMMAND as c,$isRangeSelection as s,COMMAND_PRIORITY_LOW as f,CLICK_COMMAND as u,KEY_DELETE_COMMAND as d,KEY_BACKSPACE_COMMAND as x}from"lexical";import{useRef as p,useCallback as g,useEffect as C}from"react";import{jsx as v}from"react/jsx-runtime";function N({children:N,format:h,nodeKey:y,className:D}){const[F]=e(),[L,j,B]=t(y),K=p(null),b=g((e=>{if(L&&l(a())){e.preventDefault();const r=m(y);if(n(r))return r.remove(),!0}return!1}),[L,y]);return C((()=>o(F.registerCommand(c,(e=>{if(L){const t=a();if(l(t)){const t=m(y);r(t)&&t.setFormat(e)}else if(s(t)){const o=t.getNodes();for(const t of o)if(r(t))t.setFormat(e);else{i(t).setFormat(e)}}return!0}return!1}),f),F.registerCommand(u,(e=>e.target===K.current&&(e.preventDefault(),e.shiftKey||B(),j(!L),!0)),f),F.registerCommand(d,b,f),F.registerCommand(x,b,f))),[B,F,L,y,b,j]),v("div",{className:[D.base,L?D.focus:null].filter(Boolean).join(" "),ref:K,style:{textAlign:h||void 0},children:N})}export{N as BlockWithAlignableContents};
