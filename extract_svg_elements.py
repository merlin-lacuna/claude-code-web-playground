#!/usr/bin/env python3
"""
Extract individual elements from an SVG file.
- Extracts base64 encoded images to separate files
- Extracts individual SVG elements to separate SVG files
"""

import xml.etree.ElementTree as ET
import base64
import re
import os

def extract_svg_elements(svg_file, image_dir='image_elements', svg_dir='svg_elements'):
    """Extract elements from SVG file"""

    # Parse the SVG file
    print(f"Parsing {svg_file}...")
    tree = ET.parse(svg_file)
    root = tree.getroot()

    # Define SVG namespace
    ns = {'svg': 'http://www.w3.org/2000/svg',
          'xlink': 'http://www.w3.org/1999/xlink'}

    # Create output directories
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(svg_dir, exist_ok=True)

    # Extract base64 images from symbols
    symbols = root.findall('.//svg:defs/svg:symbol', ns)
    print(f"Found {len(symbols)} symbols")

    image_count = 0
    for i, symbol in enumerate(symbols):
        symbol_id = symbol.get('id', f'symbol_{i}')

        # Find image elements with base64 data
        images = symbol.findall('.//svg:image', ns)
        for j, img in enumerate(images):
            href = img.get('href') or img.get('{http://www.w3.org/1999/xlink}href')
            if href and href.startswith('data:'):
                # Extract base64 data
                match = re.match(r'data:([^;]+);base64,(.+)', href)
                if match:
                    mime_type, b64_data = match.groups()

                    # Determine file extension
                    ext_map = {
                        'image/png': 'png',
                        'image/jpeg': 'jpg',
                        'image/jpg': 'jpg',
                        'image/svg+xml': 'svg',
                        'image/gif': 'gif'
                    }
                    ext = ext_map.get(mime_type, 'bin')

                    # Decode and save
                    filename = f"{image_dir}/{symbol_id}_{j}.{ext}"
                    with open(filename, 'wb') as f:
                        f.write(base64.b64decode(b64_data))
                    print(f"Extracted image: {filename}")
                    image_count += 1

    # Extract individual SVG elements (symbols, groups, paths, etc.)
    element_count = 0

    # Extract symbols as separate SVG files
    for i, symbol in enumerate(symbols):
        symbol_id = symbol.get('id', f'symbol_{i}')

        # Get viewBox or use default
        viewBox = symbol.get('viewBox', '0 0 100 100')

        # Create a new SVG with this symbol's content
        new_svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': viewBox,
            'version': '1.1'
        })

        # Copy all children from symbol to new SVG
        for child in symbol:
            new_svg.append(child)

        # Write to file
        filename = f"{svg_dir}/{symbol_id}.svg"
        tree_out = ET.ElementTree(new_svg)
        ET.indent(tree_out, space='  ')
        tree_out.write(filename, encoding='utf-8', xml_declaration=True)
        print(f"Extracted symbol: {filename}")
        element_count += 1

    # Extract top-level groups and elements (excluding defs)
    for i, element in enumerate(root):
        tag = element.tag.replace('{http://www.w3.org/2000/svg}', '')

        # Skip defs, metadata, and symbol elements
        if tag in ['defs', 'metadata']:
            continue

        element_id = element.get('id', f'{tag}_{i}')

        # Create a new SVG with this element
        new_svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': root.get('viewBox', '0 0 100 100'),
            'version': '1.1'
        })

        # Copy defs if they exist (for symbol references)
        defs = root.find('.//svg:defs', ns)
        if defs is not None:
            new_svg.append(defs)

        # Add the element
        new_svg.append(element)

        # Write to file
        filename = f"{svg_dir}/{element_id}.svg"
        tree_out = ET.ElementTree(new_svg)
        ET.indent(tree_out, space='  ')
        tree_out.write(filename, encoding='utf-8', xml_declaration=True)
        print(f"Extracted element: {filename}")
        element_count += 1

    print(f"\nExtraction complete!")
    print(f"Total images extracted: {image_count}")
    print(f"Total SVG elements extracted: {element_count}")

if __name__ == '__main__':
    extract_svg_elements('svgs/field-testing.svg')
