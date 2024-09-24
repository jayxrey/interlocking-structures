#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        
        # Get the selected body
        sel = ui.activeSelections.item(0)
        
        body = sel.entity
        
        # Export file dialog
        file_dialog = ui.createFileDialog()
        file_dialog.isMultiSelectEnabled = False
        file_dialog.title = 'Save .vol File'
        file_dialog.filter = 'Vol Files (*.vol)'
        dialog_result = file_dialog.showSave()

        if dialog_result != adsk.core.DialogResults.DialogOK:
            return

        file_path = file_dialog.filename
        
        # Extract data and write to .vol
        vol_data = extract_vol_data(body)
        write_vol(file_path, vol_data)

        ui.messageBox(f'Model exported to {file_path}')
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def extract_vol_data(body):
    # Define grid resolution for each axis
    grid_size_x = 10  # Adjust as needed for X-axis resolution
    grid_size_y = 8   # Adjust as needed for Y-axis resolution
    grid_size_z = 12  # Adjust as needed for Z-axis resolution

    # Initialize the voxel grid based on the individual sizes for each axis
    voxels = [[[0 for _ in range(grid_size_z)] for _ in range(grid_size_y)] for _ in range(grid_size_x)]
    
    # Define the bounding box of the body
    bounding_box = body.boundingBox
    min_point = bounding_box.minPoint
    max_point = bounding_box.maxPoint

    # Calculate voxel size for each axis based on the bounding box dimensions
    voxel_size_x = (max_point.x - min_point.x) / grid_size_x
    voxel_size_y = (max_point.y - min_point.y) / grid_size_y
    voxel_size_z = (max_point.z - min_point.z) / grid_size_z

    # Iterate over the grid to fill in voxel data
    for x in range(grid_size_x):
        for y in range(grid_size_y):
            for z in range(grid_size_z):
                # Calculate the center point of the voxel
                voxel_center = adsk.core.Point3D.create(
                    min_point.x + (x + 0.5) * voxel_size_x,
                    min_point.y + (y + 0.5) * voxel_size_y,
                    min_point.z + (z + 0.5) * voxel_size_z
                )

                # Use pointContainment to check voxel occupancy
                containment = body.pointContainment(voxel_center)
                if containment == adsk.fusion.PointContainment.PointInsidePointContainment:
                    voxels[x][y][z] = 1  # Mark voxel as occupied
                elif containment == adsk.fusion.PointContainment.PointOnPointContainment:
                    voxels[x][y][z] = 1  # You might also consider marking boundary points as occupied

    return voxels




def write_vol(file_path, vol_data):
    grid_size_x = len(vol_data)
    grid_size_y = len(vol_data[0])
    grid_size_z = len(vol_data[0][0])

    with open(file_path, 'w') as vol_file:
        vol_file.write(f"{grid_size_x} {grid_size_y} {grid_size_z}\n")  # Grid dimensions
        vol_file.write("0.4 0.4 0.4\n")  # Example voxel size, adjust as needed
        
        # Write voxel data
        for layer in vol_data:
            for row in layer:
                vol_file.write(" ".join(map(str, row)) + "\n")
