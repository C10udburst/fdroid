import os
import glob
import shutil
import xml.etree.ElementTree as ET

APKTOOL_PATH = r"java -jar apktool.jar"
CONVERT_PATH = r"convert"

def run_apktool(apk_path):
    if os.path.exists("apk.out"):
        shutil.rmtree("apk.out")
    res = os.system(f"{APKTOOL_PATH} -s -b --keep-broken-res --no-assets --force -o apk.out d {apk_path}")
    if res != 0:
        raise Exception(f"apktool failed with error code {res}")

def get_package_name():
    if not os.path.exists("apk.out"):
        raise Exception("apk.out does not exist. Run apktool first.")
    
    manifest_path = os.path.join("apk.out", "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        raise Exception("AndroidManifest.xml does not exist in apk.out. Run apktool first.")
    
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    return root.get("package")

def find_icon_name():
    if not os.path.exists("apk.out"):
        raise Exception("apk.out does not exist. Run apktool first.")
    
    manifest_path = os.path.join("apk.out", "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        raise Exception("AndroidManifest.xml does not exist in apk.out. Run apktool first.")
    
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    application = root.find("application")
    if application is None:
        raise Exception("No application tag found in AndroidManifest.xml")
    
    icon = application.get("{http://schemas.android.com/apk/res/android}icon") or application.get("{http://schemas.android.com/apk/res/android}roundIcon")
    if icon is None:
        raise Exception("No icon found in AndroidManifest.xml")
    
    return icon

def find_with_extension(icons, ext):
    for icon in icons:
        if icon.endswith(ext):
            return icon
    return None

def find_icon_path(icon_name):
    found = []
    
    if icon_name.startswith("@mipmap/"):
        icon_name = icon_name.replace("@mipmap/", "")
        for path in glob.glob(os.path.join("apk.out", "res", "mipma*/*")):
            fname = os.path.basename(path)
            if fname.startswith(icon_name):
                found.append(path)
    elif icon_name.startswith("@drawable/"):
        icon_name = icon_name.replace("@drawable/", "")
        for path in glob.glob(os.path.join("apk.out", "res", "drawabl*/*")):
            fname = os.path.basename(path)
            if fname.startswith(icon_name):
                found.append(path)
    elif icon_name.startswith("@color/"):
        icon_name = icon_name.replace("@color/", "")
        for path in glob.glob(os.path.join("apk.out", "res", "values*/colors.xml")):
            tree = ET.parse(path)
            root = tree.getroot()
            for color in root.findall("color"):
                if color.get("name") == icon_name:
                    found.append(color.text)
                    break
    elif icon_name.startswith("@android:color/"):
        found.append(icon_name.replace("@android:color/", ""))

                
    
    if path := find_with_extension(found, ".png"):
        return path
    if path := find_with_extension(found, ".webp"):
        return path
    if path := find_with_extension(found, ".xml"):
        return path
    
    for path in found:
        return path
    
    return None


def android_to_svg(android_element):
    if android_element.tag == 'path':
        path_data = android_element.get('{http://schemas.android.com/apk/res/android}pathData')
        path_fill = android_element.get('{http://schemas.android.com/apk/res/android}fillColor')
        if path_data is None:
            return None
        if path_fill is None:
            path_fill = "#000000"
        if path_fill.startswith("@android:color/"):
            path_fill = path_fill.replace("@android:color/", "")
        if path_fill.startswith("@color/"):
            path_fill = find_icon_path(path_fill)
        svg_path = ET.Element('path', {
            'd': path_data,
            'fill': path_fill
        })
        svg_path.text = ""
        return svg_path
    elif android_element.tag == 'clip-path':
        clip_path_id = android_element.get('{http://schemas.android.com/apk/res/android}name')
        
        clip_path = ET.Element('clipPath', {'id': clip_path_id})
        for subchild in android_element:
            obj = android_to_svg(subchild)
            if obj is not None:
                clip_path.append(obj)
        clip_path.text = ""
        return clip_path
    elif android_element.tag == 'group':
        group_id = android_element.get('{http://schemas.android.com/apk/res/android}name')
        group = ET.Element('g', {'id': group_id})
        group.text = ""
        for subchild in android_element:
            obj = android_to_svg(subchild)
            if obj is not None:
                group.append(obj)
        return group
    elif android_element.tag == 'vector':
        vector_width = android_element.get('{http://schemas.android.com/apk/res/android}width').replace("dp", "")
        vector_height = android_element.get('{http://schemas.android.com/apk/res/android}height').replace("dp", "")
        vector_viewport_width = android_element.get('{http://schemas.android.com/apk/res/android}viewportWidth').replace("dp", "")
        vector_viewport_height = android_element.get('{http://schemas.android.com/apk/res/android}viewportHeight').replace("dp", "")
        
        svg_vector = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': vector_width,
            'height': vector_height,
            'viewBox': f"0 0 {vector_viewport_width} {vector_viewport_height}"
        })
        
        svg_vector.text = ""
        
        for subchild in android_element:
            obj = android_to_svg(subchild)
            if obj is not None:
                svg_vector.append(obj)
        
        return svg_vector

    return None

def fix_nones(tree):
    # if any attr is None, remove it
    for elem in tree.iter():
        for attr in list(elem.attrib.keys()):
            if elem.attrib[attr] is None:
                del elem.attrib[attr]
    return tree

def join_android_vectors(vec1_root, vec2_root):
    vec_root = ET.Element('vector', {
        'xmlns:android': 'http://schemas.android.com/apk/res/android',
        '{http://schemas.android.com/apk/res/android}width': vec1_root.get('{http://schemas.android.com/apk/res/android}width'),
        '{http://schemas.android.com/apk/res/android}height': vec1_root.get('{http://schemas.android.com/apk/res/android}height'),
        '{http://schemas.android.com/apk/res/android}viewportWidth': vec1_root.get('{http://schemas.android.com/apk/res/android}viewportWidth'),
        '{http://schemas.android.com/apk/res/android}viewportHeight': vec1_root.get('{http://schemas.android.com/apk/res/android}viewportHeight')
    })
    
    for child in vec1_root:
        vec_root.append(child)
        
    for child in vec2_root:
        vec_root.append(child)
        
    return vec_root
    
    

def convert_to_png(icon_path, output_path):
    if not os.path.exists(icon_path):
        raise Exception(f"Icon path {icon_path} does not exist")
    
    if icon_path.endswith(".png"):
        shutil.copy(icon_path, output_path)
        return
    
    if icon_path.endswith(".webp"):
        res = os.system(f"{CONVERT_PATH} {icon_path} {output_path}")
        if res != 0:
            raise Exception(f"convert failed with error code {res}")
        return
    
    if icon_path.endswith(".xml"):
        tree = ET.parse(icon_path)
        root = tree.getroot()
        if root.tag == 'adaptive-icon':
            foreground = root.find('foreground')
            background = root.find('background')
            foreground_path = foreground.get('{http://schemas.android.com/apk/res/android}drawable')
            background_path = background.get('{http://schemas.android.com/apk/res/android}drawable')
            foreground_path = find_icon_path(foreground_path)
            background_path = find_icon_path(background_path)
            if foreground_path is None or background_path is None:
                raise Exception("Foreground or background path not found")
            if background_path.startswith("#"):
                background_elem = ET.Element('path', {
                    '{http://schemas.android.com/apk/res/android}pathData': 'M0,0h24v24H0z',
                    '{http://schemas.android.com/apk/res/android}fillColor': background_path
                })
                background_root = ET.Element('vector', {
                    'xmlns:android': 'http://schemas.android.com/apk/res/android',
                    '{http://schemas.android.com/apk/res/android}width': '24dp',
                    '{http://schemas.android.com/apk/res/android}height': '24dp',
                    '{http://schemas.android.com/apk/res/android}viewportWidth': '24',
                    '{http://schemas.android.com/apk/res/android}viewportHeight': '24'
                })
                background_root.append(background_elem)
            else:
                background_tree = ET.parse(background_path)
                background_root = background_tree.getroot()
            
            foreground_tree = ET.parse(foreground_path)
            foreground_root = foreground_tree.getroot()
            
            vector_xml = join_android_vectors(background_root, foreground_root)
        elif root.tag == 'vector':
            vector_xml = root
        else:
            raise Exception("Unknown XML format")
        svg_tree = android_to_svg(vector_xml)
        svg_tree = fix_nones(svg_tree)
        # resize the svg to 512x512
        svg_tree.set('width', '512')
        svg_tree.set('height', '512')
        svg_path = "icon.svg"
        svg_tree_str = ET.tostring(svg_tree, encoding='unicode')
        with open(svg_path, 'w') as f:
            f.write(svg_tree_str)
        res = os.system(f"{CONVERT_PATH} {svg_path} {output_path}")
        if res != 0:
            raise Exception(f"convert failed with error code {res}")
        os.remove(svg_path)
        return
    raise Exception("Unknown icon format")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python icon.py <apk_path> <output_folder>")
        sys.exit(1)
        
    apk_path = sys.argv[1]
    output_path = sys.argv[2]   
    run_apktool(apk_path)
    app_name = get_package_name()
    output_path = os.path.join(output_path, f"{app_name}/en-US/icon.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    convert_to_png(find_icon_path(find_icon_name()), output_path)
    print(f"Icon saved to {output_path}")
        
