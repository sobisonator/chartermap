/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */

'use strict';var a=require("@lexical/react/LexicalComposerContext"),f=require("react");let l="undefined"!==typeof window&&"undefined"!==typeof window.document&&"undefined"!==typeof window.document.createElement?f.useLayoutEffect:f.useEffect;
function m(c){let [g]=a.useLexicalComposerContext(),d=f.useMemo(()=>c(g),[g,c]),b=f.useRef(d.initialValueFn()),[n,h]=f.useState(b.current);l(()=>{let {initialValueFn:p,subscribe:q}=d,e=p();b.current!==e&&(b.current=e,h(e));return q(k=>{b.current=k;h(k)})},[d,c]);return n}exports.default=m;exports.useLexicalSubscription=m
