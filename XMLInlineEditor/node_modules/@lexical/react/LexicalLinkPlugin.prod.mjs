/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import{LinkNode as t,TOGGLE_LINK_COMMAND as r,$toggleLink as e}from"@lexical/link";import{useLexicalComposerContext as o}from"@lexical/react/LexicalComposerContext";import{mergeRegister as i,objectKlassEquals as n}from"@lexical/utils";import{COMMAND_PRIORITY_LOW as l,PASTE_COMMAND as a,$getSelection as m,$isRangeSelection as s,$isElementNode as c}from"lexical";import{useEffect as d}from"react";function u({validateUrl:u}){const[p]=o();return d((()=>{if(!p.hasNodes([t]))throw new Error("LinkPlugin: LinkNode not registered on editor");return i(p.registerCommand(r,(t=>{if(null===t)return e(t),!0;if("string"==typeof t)return!(void 0!==u&&!u(t))&&(e(t),!0);{const{url:r,target:o,rel:i,title:n}=t;return e(r,{rel:i,target:o,title:n}),!0}}),l),void 0!==u?p.registerCommand(a,(t=>{const e=m();if(!s(e)||e.isCollapsed()||!n(t,ClipboardEvent))return!1;const o=t;if(null===o.clipboardData)return!1;const i=o.clipboardData.getData("text");return!!u(i)&&(!e.getNodes().some((t=>c(t)))&&(p.dispatchCommand(r,i),t.preventDefault(),!0))}),l):()=>{})}),[p,u]),null}export{u as LinkPlugin};
