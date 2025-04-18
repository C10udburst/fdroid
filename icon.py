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
    if path := find_with_extension(found, ".jpg"):
        return path
    if path := find_with_extension(found, ".xml"):
        return path
    
    for path in found:
        return path
    
    return None


def remap_tree(tree, map, tag_name):
    attribs = {}
    for elem in tree.iter():
        for attr in list(elem.attrib.keys()):
            if attr in map:
                val = elem.attrib[attr]
                if val.startswith("@android:color/"):
                    val = val.replace("@android:color/", "")
                if val.startswith("@color/"):
                    val = find_icon_path(val)
                if val.startswith("#") and len(val) == 9:
                    val = "#" + val[3:]
                if val.endswith("dp"):
                    val = val.replace("dp", "")
                if val.endswith("dip"):
                    val = val.replace("dip", "")
                attribs[map[attr]] = val
    return ET.Element(tag_name, attribs)

def android_to_svg(android_element):
    if android_element.tag == 'path':
        map = {
            '{http://schemas.android.com/apk/res/android}pathData': 'd',
            '{http://schemas.android.com/apk/res/android}fillColor': 'fill',
            '{http://schemas.android.com/apk/res/android}strokeColor': 'stroke',
            '{http://schemas.android.com/apk/res/android}strokeWidth': 'stroke-width',
        }
        svg_path = remap_tree(android_element, map, 'path')
        return svg_path
    elif android_element.tag == 'group':
        map = {
            '{http://schemas.android.com/apk/res/android}name': 'id',
        }
        group = remap_tree(android_element, map, 'g')
        
        translateX = android_element.get('{http://schemas.android.com/apk/res/android}translateX')
        translateY = android_element.get('{http://schemas.android.com/apk/res/android}translateY')
        scaleX = android_element.get('{http://schemas.android.com/apk/res/android}scaleX')
        scaleY = android_element.get('{http://schemas.android.com/apk/res/android}scaleY')
        
        transform = ""
        if translateX is not None and translateY is not None:
            transform += f"translate({translateX}, {translateY}) "
        if scaleX is not None and scaleY is not None:
            transform += f"scale({scaleX}, {scaleY}) "
        if transform:
            transform = transform.strip()
            android_element.set('transform', transform)
        for subchild in android_element:
            obj = android_to_svg(subchild)
            if obj is not None:
                group.append(obj)
        return group
    elif android_element.tag == 'vector':
        map = {
            '{http://schemas.android.com/apk/res/android}width': 'width',
            '{http://schemas.android.com/apk/res/android}height': 'height',
            '{http://schemas.android.com/apk/res/android}tint': 'fill',
        }
        
        svg_vector = remap_tree(android_element, map, 'svg')
        svg_vector.set('xmlns', 'http://www.w3.org/2000/svg')
        
        vector_viewport_width = android_element.get('{http://schemas.android.com/apk/res/android}viewportWidth').replace("dp", "")
        vector_viewport_height = android_element.get('{http://schemas.android.com/apk/res/android}viewportHeight').replace("dp", "")
        viewBox = f"0 0 {vector_viewport_width} {vector_viewport_height}"
        svg_vector.set('viewBox', viewBox)
        
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

def add_background_color(tree, color):
    w = tree.get('{http://schemas.android.com/apk/res/android}viewportWidth').replace("dp", "")
    h = tree.get('{http://schemas.android.com/apk/res/android}viewportWidth').replace("dp", "")
    
    rect = ET.Element('path', {
        '{http://schemas.android.com/apk/res/android}pathData': f'M0,0h{w}v{h}H0z',
        '{http://schemas.android.com/apk/res/android}fillColor': color,
    })
    
    tree.insert(0, rect)
    return tree

def add_background_tree(tree, background_tree):
    for elem in background_tree[::-1]:
        tree.insert(0, elem) 
    return tree
    
    

def convert_to_png(icon_path, output_path):
    if not os.path.exists(icon_path):
        raise Exception(f"Icon path {icon_path} does not exist")
    
    if icon_path.endswith(".png"):
        shutil.copy(icon_path, output_path)
        return
    
    if icon_path.endswith(".webp") or icon_path.endswith(".jpg"):
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
            
            foreground_tree = ET.parse(foreground_path)
            foreground_root = foreground_tree.getroot()
            
            if foreground_path is None or background_path is None:
                raise Exception("Foreground or background path not found")
            if background_path.startswith("#"):
                foreground_root = add_background_color(foreground_root, background_path)
            else:
                background_tree = ET.parse(background_path)
                background_root = background_tree.getroot()
                foreground_root = add_background_tree(foreground_root, background_tree)
            vector_xml = foreground_root
        elif root.tag == 'vector':
            vector_xml = root
        else:
            raise Exception("Unknown XML format")
        svg_tree = android_to_svg(vector_xml)
        svg_tree = fix_nones(svg_tree)
        svg_tree.set('width', '512')
        svg_tree.set('height', '512')
        svg_path = "icon.svg"
        svg_tree_str = ET.tostring(svg_tree, encoding='unicode')
        with open(svg_path, 'w') as f:
            f.write(svg_tree_str)
        res = os.system(f"{CONVERT_PATH} {svg_path} {output_path}")
        if res != 0:
            raise Exception(f"convert failed with error code {res}")
        #os.remove(svg_path)
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
    shutil.rmtree("apk.out")
