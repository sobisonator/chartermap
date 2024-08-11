/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
 */
/// <reference types="react" />
import type { Props as ElementProps } from './shared/LexicalContentEditableElement';
import type { LexicalEditor } from 'lexical';
export type Props = Omit<ElementProps, 'editor'> & {
    editor__DEPRECATED?: LexicalEditor;
} & ({
    'aria-placeholder'?: void;
    placeholder?: null;
} | {
    'aria-placeholder': string;
    placeholder: ((isEditable: boolean) => null | JSX.Element) | JSX.Element;
});
export declare const ContentEditable: import("react").ForwardRefExoticComponent<Props & import("react").RefAttributes<HTMLDivElement>>;
