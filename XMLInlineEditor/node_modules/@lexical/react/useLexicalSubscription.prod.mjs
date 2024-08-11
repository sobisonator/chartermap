/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

import{useLexicalComposerContext as e}from"@lexical/react/LexicalComposerContext";import{useLayoutEffect as t,useEffect as n,useMemo as r,useRef as o,useState as i}from"react";const c="undefined"!=typeof window&&void 0!==window.document&&void 0!==window.document.createElement?t:n;function u(t){const[n]=e(),u=r((()=>t(n)),[n,t]),a=o(u.initialValueFn()),[d,l]=i(a.current);return c((()=>{const{initialValueFn:e,subscribe:t}=u,n=e();return a.current!==n&&(a.current=n,l(n)),t((e=>{a.current=e,l(e)}))}),[u,t]),d}export{u as default,u as useLexicalSubscription};
