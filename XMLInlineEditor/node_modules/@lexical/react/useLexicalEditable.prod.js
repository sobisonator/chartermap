/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';var b=require("@lexical/react/LexicalComposerContext"),k=require("react");let l="undefined"!==typeof window&&"undefined"!==typeof window.document&&"undefined"!==typeof window.document.createElement?k.useLayoutEffect:k.useEffect;
function m(a){let [c]=b.useLexicalComposerContext(),e=k.useMemo(()=>a(c),[c,a]),d=k.useRef(e.initialValueFn()),[p,g]=k.useState(d.current);l(()=>{let {initialValueFn:q,subscribe:r}=e,f=q();d.current!==f&&(d.current=f,g(f));return r(h=>{d.current=h;g(h)})},[e,a]);return p}function n(a){return{initialValueFn:()=>a.isEditable(),subscribe:c=>a.registerEditableListener(c)}}function t(){return m(n)}exports.default=t;exports.useLexicalEditable=t
