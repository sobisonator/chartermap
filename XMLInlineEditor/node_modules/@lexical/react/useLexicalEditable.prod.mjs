/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import{useLexicalComposerContext as e}from"@lexical/react/LexicalComposerContext";import{useLayoutEffect as t,useEffect as n,useMemo as r,useRef as i,useState as o}from"react";const u="undefined"!=typeof window&&void 0!==window.document&&void 0!==window.document.createElement?t:n;function c(e){return{initialValueFn:()=>e.isEditable(),subscribe:t=>e.registerEditableListener(t)}}function a(){return function(t){const[n]=e(),c=r((()=>t(n)),[n,t]),a=i(c.initialValueFn()),[l,d]=o(a.current);return u((()=>{const{initialValueFn:e,subscribe:t}=c,n=e();return a.current!==n&&(a.current=n,d(n)),t((e=>{a.current=e,d(e)}))}),[c,t]),l}(c)}export{a as default,a as useLexicalEditable};
