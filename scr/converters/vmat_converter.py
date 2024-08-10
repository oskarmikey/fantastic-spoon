import os
import logging
from file_handler.vmt_parser import parse_vmt_file
from file_handler.file_operations import find_texture_file, copy_to_backup_and_delete

def convert_vmt_to_vmat(vmt_file, base_path, texture_format, generate_height, generate_normal):
    parameters = parse_vmt_file(vmt_file)
    logging.info(f"Processing VMT file: {vmt_file}")

    base_texture_name = parameters.get('$basetexture', '').replace('"', '')
    bumpmap_texture_name = parameters.get('$bumpmap', '').replace('"', '')
    normalmap_texture_name = parameters.get('$normalmap', '').replace('"', '')
    roughness_texture_name = f"{base_texture_name}_roughness.{texture_format}"
    parameters['$roughness'] = roughness_texture_name

    normal_map_path = None
    height_map_path = None

    if bumpmap_texture_name and "-ssbump" in bumpmap_texture_name:
        bumpmap_file_path = find_texture_file(bumpmap_texture_name, base_path, texture_format)
        if bumpmap_file_path:
            logging.info(f"Converting ssbump map to normal and height maps for: {bumpmap_texture_name}")
            normal_map_path, height_map_path = convert_ssbump_to_normal_and_height(bumpmap_file_path, texture_format)

    vmat_file = vmt_file.replace('.vmt', '.vmat')
    vmat_file_export = os.path.join(base_path, vmat_file)

    try:
        with open(vmat_file_export, "w") as file:
            file.write("// THIS FILE IS AUTO-GENERATED\n\n")
            file.write("Layer0\n{\n")
            file.write('\tshader "csgo_environment.vfx"\n\n')

            # Add other parameters if available
            file.write('\t//---- Color ----\n')
            file.write('\tg_flModelTintAmount "1.000"\n')
            file.write('\tg_nScaleTexCoordUByModelScaleAxis "0" // None\n')
            file.write('\tg_nScaleTexCoordVByModelScaleAxis "0" // None\n')
            file.write('\tg_vColorTint "[1.000000 1.000000 1.000000 0.000000]"\n\n')

            file.write('\t//---- Fog ----\n')
            file.write('\tg_bFogEnabled "1"\n\n')

            file.write('\t//---- Material1 ----\n')
            file.write('\tg_flTexCoordRotation1 "0.000"\n')
            file.write('\tg_vTexCoordCenter1 "[0.500 0.500]"\n')
            file.write('\tg_vTexCoordOffset1 "[0.000 0.000]"\n')
            file.write('\tg_vTexCoordScale1 "[1.000 1.000]"\n')
            if '$basetexture' in parameters:
                file.write(f'\tTextureColor1 "materials/{parameters["$basetexture"].lower().replace("\\", "/")}.{texture_format}"\n')
            if normal_map_path:
                file.write(f'\tTextureNormal1 "materials/{normal_map_path.replace("\\", "/")}"\n')
            elif bumpmap_texture_name and generate_normal:
                file.write(f'\tTextureNormal1 "materials/{bumpmap_texture_name.lower().replace("-ssbump", "_normal").replace("\\", "/")}.{texture_format}"\n')
            else:
                file.write(f'\tTextureNormal1 "materials/default/default_normal.{texture_format}"\n')
            if generate_height and height_map_path:
                file.write(f'\tTextureHeight1 "materials/{height_map_path.replace("\\", "/")}"\n')
            file.write('\tTextureMetalness1 "materials/default/default_metal.tga"\n')
            file.write(f'\tTextureRoughness1 "materials/{roughness_texture_name.lower().replace("\\", "/")}"\n')
            file.write('\tTextureTintMask1 "materials/default/default_mask.tga"\n\n')

            file.write('\t//---- Texture Address Mode ----\n')
            file.write('\tg_nTextureAddressModeU "0" // Wrap\n')
            file.write('\tg_nTextureAddressModeV "0" // Wrap\n')

            file.write("}\n")
        logging.info(f"VMAT file generated: {vmat_file_export}")
    except Exception as e:
        logging.error(f"Error writing VMAT file {vmat_file_export}: {e}")

    return vmat_file_export
