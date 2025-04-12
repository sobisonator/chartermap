<?php
/**
 * Plugin Name: Overlapping Markup Editor
 * Plugin URI: https://github.com/sobisonator/chartermap
 * Description: This plugin lets you add and edit overlappng markup objects on a text
 * Version: 0.0.1
 * Author: Carlos Austin-Gonzalez
 * Author URI: N/A
 * License: GPL-3.0
 */
add_action("wp_head", "overlapping_markup_editor");
function overlapping_markup_editor( ){
    echo "Overlapping markup editor is active";
}