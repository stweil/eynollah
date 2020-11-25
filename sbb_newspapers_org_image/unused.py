"""
Unused methods from eynollah
"""

import numpy as np
from shapely import geometry
import cv2

def color_images_diva(seg, n_classes):
    """
    XXX unused
    """
    ann_u = range(n_classes)
    if len(np.shape(seg)) == 3:
        seg = seg[:, :, 0]

    seg_img = np.zeros((np.shape(seg)[0], np.shape(seg)[1], 3)).astype(float)
    # colors=sns.color_palette("hls", n_classes)
    colors = [[1, 0, 0], [8, 0, 0], [2, 0, 0], [4, 0, 0]]

    for c in ann_u:
        c = int(c)
        segl = seg == c
        seg_img[:, :, 0][seg == c] = colors[c][0]  # segl*(colors[c][0])
        seg_img[:, :, 1][seg == c] = colors[c][1]  # seg_img[:,:,1]=segl*(colors[c][1])
        seg_img[:, :, 2][seg == c] = colors[c][2]  # seg_img[:,:,2]=segl*(colors[c][2])
    return seg_img

def find_polygons_size_filter(contours, median_area, scaler_up=1.2, scaler_down=0.8):
    """
    XXX unused
    """
    found_polygons_early = list()

    for c in contours:
        if len(c) < 3:  # A polygon cannot have less than 3 points
            continue

        polygon = geometry.Polygon([point[0] for point in c])
        area = polygon.area
        # Check that polygon has area greater than minimal area
        if area >= median_area * scaler_down and area <= median_area * scaler_up:
            found_polygons_early.append(np.array([point for point in polygon.exterior.coords], dtype=np.uint))
    return found_polygons_early

def resize_ann(seg_in, input_height, input_width):
    """
    XXX unused
    """
    return cv2.resize(seg_in, (input_width, input_height), interpolation=cv2.INTER_NEAREST)

def get_one_hot(seg, input_height, input_width, n_classes):
    seg = seg[:, :, 0]
    seg_f = np.zeros((input_height, input_width, n_classes))
    for j in range(n_classes):
        seg_f[:, :, j] = (seg == j).astype(int)
    return seg_f

def color_images(seg, n_classes):
    ann_u = range(n_classes)
    if len(np.shape(seg)) == 3:
        seg = seg[:, :, 0]

    seg_img = np.zeros((np.shape(seg)[0], np.shape(seg)[1], 3)).astype(np.uint8)
    colors = sns.color_palette("hls", n_classes)

    for c in ann_u:
        c = int(c)
        segl = seg == c
        seg_img[:, :, 0] = segl * c
        seg_img[:, :, 1] = segl * c
        seg_img[:, :, 2] = segl * c
    return seg_img

def cleaning_probs(probs: np.ndarray, sigma: float) -> np.ndarray:
    # Smooth
    if sigma > 0.0:
        return cv2.GaussianBlur(probs, (int(3 * sigma) * 2 + 1, int(3 * sigma) * 2 + 1), sigma)
    elif sigma == 0.0:
        return cv2.fastNlMeansDenoising((probs * 255).astype(np.uint8), h=20) / 255
    else:  # Negative sigma, do not do anything
        return probs


def early_deskewing_slope_calculation_based_on_lines(region_pre_p):
    # lines are labels by 6 in this model
    seperators_closeup = ((region_pre_p[:, :, :] == 6)) * 1

    seperators_closeup = seperators_closeup.astype(np.uint8)
    imgray = cv2.cvtColor(seperators_closeup, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

    contours_lines, hierachy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    slope_lines, dist_x, x_min_main, x_max_main, cy_main, slope_lines_org, y_min_main, y_max_main, cx_main = find_features_of_lines(contours_lines)

    slope_lines_org_hor = slope_lines_org[slope_lines == 0]
    args = np.array(range(len(slope_lines)))
    len_x = seperators_closeup.shape[1] / 4.0

    args_hor = args[slope_lines == 0]
    dist_x_hor = dist_x[slope_lines == 0]
    x_min_main_hor = x_min_main[slope_lines == 0]
    x_max_main_hor = x_max_main[slope_lines == 0]
    cy_main_hor = cy_main[slope_lines == 0]

    args_hor = args_hor[dist_x_hor >= len_x / 2.0]
    x_max_main_hor = x_max_main_hor[dist_x_hor >= len_x / 2.0]
    x_min_main_hor = x_min_main_hor[dist_x_hor >= len_x / 2.0]
    cy_main_hor = cy_main_hor[dist_x_hor >= len_x / 2.0]
    slope_lines_org_hor = slope_lines_org_hor[dist_x_hor >= len_x / 2.0]

    slope_lines_org_hor = slope_lines_org_hor[np.abs(slope_lines_org_hor) < 1.2]
    slope_mean_hor = np.mean(slope_lines_org_hor)

    if np.abs(slope_mean_hor) > 1.2:
        slope_mean_hor = 0

    # deskewed_new=rotate_image(image_regions_eraly_p[:,:,:],slope_mean_hor)

    args_ver = args[slope_lines == 1]
    y_min_main_ver = y_min_main[slope_lines == 1]
    y_max_main_ver = y_max_main[slope_lines == 1]
    x_min_main_ver = x_min_main[slope_lines == 1]
    x_max_main_ver = x_max_main[slope_lines == 1]
    cx_main_ver = cx_main[slope_lines == 1]
    dist_y_ver = y_max_main_ver - y_min_main_ver
    len_y = seperators_closeup.shape[0] / 3.0

    return slope_mean_hor, cx_main_ver, dist_y_ver

def boosting_text_only_regions_by_header(textregion_pre_np, img_only_text):
    result = ((img_only_text[:, :] == 1) | (textregion_pre_np[:, :, 0] == 2)) * 1
    return result

def return_rotated_contours(slope, img_patch):
    dst = rotate_image(img_patch, slope)
    dst = dst.astype(np.uint8)
    dst = dst[:, :, 0]
    dst[dst != 0] = 1

    imgray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(imgray, 0, 255, 0)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_textlines_for_each_textregions(self, textline_mask_tot, boxes):
    textline_mask_tot = cv2.erode(textline_mask_tot, self.kernel, iterations=1)
    self.area_of_cropped = []
    self.all_text_region_raw = []
    for jk in range(len(boxes)):
        crop_img, crop_coor = crop_image_inside_box(boxes[jk], np.repeat(textline_mask_tot[:, :, np.newaxis], 3, axis=2))
        crop_img = crop_img.astype(np.uint8)
        self.all_text_region_raw.append(crop_img[:, :, 0])
        self.area_of_cropped.append(crop_img.shape[0] * crop_img.shape[1])

def deskew_region_prediction(regions_prediction, slope):
    image_regions_deskewd = np.zeros(regions_prediction[:, :].shape)
    for ind in np.unique(regions_prediction[:, :]):
        interest_reg = (regions_prediction[:, :] == ind) * 1
        interest_reg = interest_reg.astype(np.uint8)
        deskewed_new = rotate_image(interest_reg, slope)
        deskewed_new = deskewed_new[:, :]
        deskewed_new[deskewed_new != 0] = ind

        image_regions_deskewd = image_regions_deskewd + deskewed_new
    return image_regions_deskewd

def deskew_erarly(textline_mask):
    textline_mask_org = np.copy(textline_mask)
    # print(textline_mask.shape,np.unique(textline_mask),'hizzzzz')
    # slope_new=0#deskew_images(img_patch)

    textline_mask = np.repeat(textline_mask[:, :, np.newaxis], 3, axis=2) * 255

    textline_mask = textline_mask.astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)

    imgray = cv2.cvtColor(textline_mask, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

    contours, hirarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # print(hirarchy)

    commenst_contours = filter_contours_area_of_image(thresh, contours, hirarchy, max_area=0.01, min_area=0.003)
    main_contours = filter_contours_area_of_image(thresh, contours, hirarchy, max_area=1, min_area=0.003)
    interior_contours = filter_contours_area_of_image_interiors(thresh, contours, hirarchy, max_area=1, min_area=0)

    img_comm = np.zeros(thresh.shape)
    img_comm_in = cv2.fillPoly(img_comm, pts=main_contours, color=(255, 255, 255))
    ###img_comm_in=cv2.fillPoly(img_comm, pts =interior_contours, color=(0,0,0))

    img_comm_in = np.repeat(img_comm_in[:, :, np.newaxis], 3, axis=2)
    img_comm_in = img_comm_in.astype(np.uint8)

    imgray = cv2.cvtColor(img_comm_in, cv2.COLOR_BGR2GRAY)
    ##imgray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    ##mask = cv2.inRange(imgray, lower_blue, upper_blue)
    ret, thresh = cv2.threshold(imgray, 0, 255, 0)
    # print(np.unique(mask))
    ##ret, thresh = cv2.threshold(imgray, 0, 255, 0)

    ##plt.imshow(thresh)
    ##plt.show()

    contours, hirarchy = cv2.findContours(thresh.copy(), cv2.cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    areas = [cv2.contourArea(contours[jj]) for jj in range(len(contours))]

    median_area = np.mean(areas)
    contours_slope = contours  # self.find_polugons_size_filter(contours,median_area=median_area,scaler_up=100,scaler_down=0.5)

    if len(contours_slope) > 0:
        for jv in range(len(contours_slope)):
            new_poly = list(contours_slope[jv])
            if jv == 0:
                merged_all = new_poly
            else:
                merged_all = merged_all + new_poly

        merge = np.array(merged_all)

        img_in = np.zeros(textline_mask.shape)
        img_p_in = cv2.fillPoly(img_in, pts=[merge], color=(255, 255, 255))

        ##plt.imshow(img_p_in)
        ##plt.show()

        rect = cv2.minAreaRect(merge)

        box = cv2.boxPoints(rect)

        box = np.int0(box)

        indexes = [0, 1, 2, 3]
        x_list = box[:, 0]
        y_list = box[:, 1]

        index_y_sort = np.argsort(y_list)

        index_upper_left = index_y_sort[np.argmin(x_list[index_y_sort[0:2]])]
        index_upper_right = index_y_sort[np.argmax(x_list[index_y_sort[0:2]])]

        index_lower_left = index_y_sort[np.argmin(x_list[index_y_sort[2:]]) + 2]
        index_lower_right = index_y_sort[np.argmax(x_list[index_y_sort[2:]]) + 2]

        alpha1 = float(box[index_upper_right][1] - box[index_upper_left][1]) / (float(box[index_upper_right][0] - box[index_upper_left][0]))
        alpha2 = float(box[index_lower_right][1] - box[index_lower_left][1]) / (float(box[index_lower_right][0] - box[index_lower_left][0]))

        slope_true = (alpha1 + alpha2) / 2.0

        # slope=0#slope_true/np.pi*180

        # if abs(slope)>=1:
        # slope=0

        # dst=rotate_image(textline_mask,slope_true)
        # dst=dst[:,:,0]
        # dst[dst!=0]=1
    image_regions_deskewd = np.zeros(textline_mask_org[:, :].shape)
    for ind in np.unique(textline_mask_org[:, :]):
        interest_reg = (textline_mask_org[:, :] == ind) * 1
        interest_reg = interest_reg.astype(np.uint8)
        deskewed_new = rotate_image(interest_reg, slope_true)
        deskewed_new = deskewed_new[:, :]
        deskewed_new[deskewed_new != 0] = ind

        image_regions_deskewd = image_regions_deskewd + deskewed_new
    return image_regions_deskewd, slope_true

def get_all_image_patches_coordination(self, image_page):
    self.all_box_coord = []
    for jk in range(len(self.boxes)):
        _, crop_coor = crop_image_inside_box(self.boxes[jk], image_page)
        self.all_box_coord.append(crop_coor)

def find_num_col_olddd(self, regions_without_seperators, sigma_, multiplier=3.8):
    regions_without_seperators_0 = regions_without_seperators[:, :].sum(axis=1)

    meda_n_updown = regions_without_seperators_0[len(regions_without_seperators_0) :: -1]

    first_nonzero = next((i for i, x in enumerate(regions_without_seperators_0) if x), 0)
    last_nonzero = next((i for i, x in enumerate(meda_n_updown) if x), 0)

    last_nonzero = len(regions_without_seperators_0) - last_nonzero

    y = regions_without_seperators_0  # [first_nonzero:last_nonzero]

    y_help = np.zeros(len(y) + 20)

    y_help[10 : len(y) + 10] = y

    x = np.array(range(len(y)))

    zneg_rev = -y_help + np.max(y_help)

    zneg = np.zeros(len(zneg_rev) + 20)

    zneg[10 : len(zneg_rev) + 10] = zneg_rev

    z = gaussian_filter1d(y, sigma_)
    zneg = gaussian_filter1d(zneg, sigma_)

    peaks_neg, _ = find_peaks(zneg, height=0)
    peaks, _ = find_peaks(z, height=0)

    peaks_neg = peaks_neg - 10 - 10

    last_nonzero = last_nonzero - 0  # 100
    first_nonzero = first_nonzero + 0  # +100

    peaks_neg = peaks_neg[(peaks_neg > first_nonzero) & (peaks_neg < last_nonzero)]

    peaks = peaks[(peaks > 0.06 * regions_without_seperators.shape[1]) & (peaks < 0.94 * regions_without_seperators.shape[1])]

    interest_pos = z[peaks]

    interest_pos = interest_pos[interest_pos > 10]

    interest_neg = z[peaks_neg]

    if interest_neg[0] < 0.1:
        interest_neg = interest_neg[1:]
    if interest_neg[len(interest_neg) - 1] < 0.1:
        interest_neg = interest_neg[: len(interest_neg) - 1]

    min_peaks_pos = np.min(interest_pos)
    min_peaks_neg = 0  # np.min(interest_neg)

    dis_talaei = (min_peaks_pos - min_peaks_neg) / multiplier
    grenze = min_peaks_pos - dis_talaei  # np.mean(y[peaks_neg[0]:peaks_neg[len(peaks_neg)-1]])-np.std(y[peaks_neg[0]:peaks_neg[len(peaks_neg)-1]])/2.0

    interest_neg_fin = interest_neg  # [(interest_neg<grenze)]
    peaks_neg_fin = peaks_neg  # [(interest_neg<grenze)]
    interest_neg_fin = interest_neg  # [(interest_neg<grenze)]

    num_col = (len(interest_neg_fin)) + 1

    p_l = 0
    p_u = len(y) - 1
    p_m = int(len(y) / 2.0)
    p_g_l = int(len(y) / 3.0)
    p_g_u = len(y) - int(len(y) / 3.0)

    diff_peaks = np.abs(np.diff(peaks_neg_fin))
    diff_peaks_annormal = diff_peaks[diff_peaks < 30]

    return interest_neg_fin

def return_regions_without_seperators_new(self, regions_pre, regions_only_text):
    kernel = np.ones((5, 5), np.uint8)

    regions_without_seperators = ((regions_pre[:, :] != 6) & (regions_pre[:, :] != 0) & (regions_pre[:, :] != 1) & (regions_pre[:, :] != 2)) * 1

    # plt.imshow(regions_without_seperators)
    # plt.show()

    regions_without_seperators_n = ((regions_without_seperators[:, :] == 1) | (regions_only_text[:, :] == 1)) * 1

    # regions_without_seperators=( (image_regions_eraly_p[:,:,:]!=6) & (image_regions_eraly_p[:,:,:]!=0) & (image_regions_eraly_p[:,:,:]!=5) & (image_regions_eraly_p[:,:,:]!=8) & (image_regions_eraly_p[:,:,:]!=7))*1

    regions_without_seperators_n = regions_without_seperators_n.astype(np.uint8)

    regions_without_seperators_n = cv2.erode(regions_without_seperators_n, kernel, iterations=6)

    return regions_without_seperators_n

def find_images_contours_and_replace_table_and_graphic_pixels_by_image(region_pre_p):

    # pixels of images are identified by 5
    cnts_images = (region_pre_p[:, :, 0] == 5) * 1
    cnts_images = cnts_images.astype(np.uint8)
    cnts_images = np.repeat(cnts_images[:, :, np.newaxis], 3, axis=2)
    imgray = cv2.cvtColor(cnts_images, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 0, 255, 0)
    contours_imgs, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_imgs = return_parent_contours(contours_imgs, hiearchy)
    # print(len(contours_imgs),'contours_imgs')
    contours_imgs = filter_contours_area_of_image_tables(thresh, contours_imgs, hiearchy, max_area=1, min_area=0.0003)

    # print(len(contours_imgs),'contours_imgs')

    boxes_imgs = return_bonding_box_of_contours(contours_imgs)

    for i in range(len(boxes_imgs)):
        x1 = int(boxes_imgs[i][0])
        x2 = int(boxes_imgs[i][0] + boxes_imgs[i][2])
        y1 = int(boxes_imgs[i][1])
        y2 = int(boxes_imgs[i][1] + boxes_imgs[i][3])
        region_pre_p[y1:y2, x1:x2, 0][region_pre_p[y1:y2, x1:x2, 0] == 8] = 5
        region_pre_p[y1:y2, x1:x2, 0][region_pre_p[y1:y2, x1:x2, 0] == 7] = 5
    return region_pre_p

def order_and_id_of_texts_old(found_polygons_text_region, matrix_of_orders, indexes_sorted):
    id_of_texts = []
    order_of_texts = []
    index_b = 0
    for mm in range(len(found_polygons_text_region)):
        id_of_texts.append("r" + str(index_b))
        index_matrix = matrix_of_orders[:, 0][(matrix_of_orders[:, 1] == 1) & (matrix_of_orders[:, 4] == mm)]
        order_of_texts.append(np.where(indexes_sorted == index_matrix)[0][0])

        index_b += 1

    order_of_texts
    return order_of_texts, id_of_texts

def order_of_regions_old(textline_mask, contours_main):
    mada_n = textline_mask.sum(axis=1)
    y = mada_n[:]

    y_help = np.zeros(len(y) + 40)
    y_help[20 : len(y) + 20] = y
    x = np.array(range(len(y)))

    peaks_real, _ = find_peaks(gaussian_filter1d(y, 3), height=0)

    sigma_gaus = 8

    z = gaussian_filter1d(y_help, sigma_gaus)
    zneg_rev = -y_help + np.max(y_help)

    zneg = np.zeros(len(zneg_rev) + 40)
    zneg[20 : len(zneg_rev) + 20] = zneg_rev
    zneg = gaussian_filter1d(zneg, sigma_gaus)

    peaks, _ = find_peaks(z, height=0)
    peaks_neg, _ = find_peaks(zneg, height=0)

    peaks_neg = peaks_neg - 20 - 20
    peaks = peaks - 20

    if contours_main != None:
        areas_main = np.array([cv2.contourArea(contours_main[j]) for j in range(len(contours_main))])
        M_main = [cv2.moments(contours_main[j]) for j in range(len(contours_main))]
        cx_main = [(M_main[j]["m10"] / (M_main[j]["m00"] + 1e-32)) for j in range(len(M_main))]
        cy_main = [(M_main[j]["m01"] / (M_main[j]["m00"] + 1e-32)) for j in range(len(M_main))]
        x_min_main = np.array([np.min(contours_main[j][:, 0, 0]) for j in range(len(contours_main))])
        x_max_main = np.array([np.max(contours_main[j][:, 0, 0]) for j in range(len(contours_main))])

        y_min_main = np.array([np.min(contours_main[j][:, 0, 1]) for j in range(len(contours_main))])
        y_max_main = np.array([np.max(contours_main[j][:, 0, 1]) for j in range(len(contours_main))])

    if contours_main != None:
        indexer_main = np.array(range(len(contours_main)))

    if contours_main != None:
        len_main = len(contours_main)
    else:
        len_main = 0

    matrix_of_orders = np.zeros((len_main, 5))

    matrix_of_orders[:, 0] = np.array(range(len_main))

    matrix_of_orders[:len_main, 1] = 1
    matrix_of_orders[len_main:, 1] = 2

    matrix_of_orders[:len_main, 2] = cx_main
    matrix_of_orders[:len_main, 3] = cy_main

    matrix_of_orders[:len_main, 4] = np.array(range(len_main))

    peaks_neg_new = []
    peaks_neg_new.append(0)
    for iii in range(len(peaks_neg)):
        peaks_neg_new.append(peaks_neg[iii])
    peaks_neg_new.append(textline_mask.shape[0])

    final_indexers_sorted = []
    for i in range(len(peaks_neg_new) - 1):
        top = peaks_neg_new[i]
        down = peaks_neg_new[i + 1]

        indexes_in = matrix_of_orders[:, 0][(matrix_of_orders[:, 3] >= top) & ((matrix_of_orders[:, 3] < down))]
        cxs_in = matrix_of_orders[:, 2][(matrix_of_orders[:, 3] >= top) & ((matrix_of_orders[:, 3] < down))]

        sorted_inside = np.argsort(cxs_in)

        ind_in_int = indexes_in[sorted_inside]

        for j in range(len(ind_in_int)):
            final_indexers_sorted.append(int(ind_in_int[j]))

    return final_indexers_sorted, matrix_of_orders

def remove_headers_and_mains_intersection(seperators_closeup_n, img_revised_tab, boxes):
    for ind in range(len(boxes)):
        asp = np.zeros((img_revised_tab[:, :, 0].shape[0], seperators_closeup_n[:, :, 0].shape[1]))
        asp[int(boxes[ind][2]) : int(boxes[ind][3]), int(boxes[ind][0]) : int(boxes[ind][1])] = img_revised_tab[int(boxes[ind][2]) : int(boxes[ind][3]), int(boxes[ind][0]) : int(boxes[ind][1]), 0]

        head_patch_con = (asp[:, :] == 2) * 1
        main_patch_con = (asp[:, :] == 1) * 1
        # print(head_patch_con)
        head_patch_con = head_patch_con.astype(np.uint8)
        main_patch_con = main_patch_con.astype(np.uint8)

        head_patch_con = np.repeat(head_patch_con[:, :, np.newaxis], 3, axis=2)
        main_patch_con = np.repeat(main_patch_con[:, :, np.newaxis], 3, axis=2)

        imgray = cv2.cvtColor(head_patch_con, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 0, 255, 0)

        contours_head_patch_con, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_head_patch_con = return_parent_contours(contours_head_patch_con, hiearchy)

        imgray = cv2.cvtColor(main_patch_con, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 0, 255, 0)

        contours_main_patch_con, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_main_patch_con = return_parent_contours(contours_main_patch_con, hiearchy)

        y_patch_head_min, y_patch_head_max, _ = find_features_of_contours(contours_head_patch_con)
        y_patch_main_min, y_patch_main_max, _ = find_features_of_contours(contours_main_patch_con)

        for i in range(len(y_patch_head_min)):
            for j in range(len(y_patch_main_min)):
                if y_patch_head_max[i] > y_patch_main_min[j] and y_patch_head_min[i] < y_patch_main_min[j]:
                    y_down = y_patch_head_max[i]
                    y_up = y_patch_main_min[j]

                    patch_intersection = np.zeros(asp.shape)
                    patch_intersection[y_up:y_down, :] = asp[y_up:y_down, :]

                    head_patch_con = (patch_intersection[:, :] == 2) * 1
                    main_patch_con = (patch_intersection[:, :] == 1) * 1
                    head_patch_con = head_patch_con.astype(np.uint8)
                    main_patch_con = main_patch_con.astype(np.uint8)

                    head_patch_con = np.repeat(head_patch_con[:, :, np.newaxis], 3, axis=2)
                    main_patch_con = np.repeat(main_patch_con[:, :, np.newaxis], 3, axis=2)

                    imgray = cv2.cvtColor(head_patch_con, cv2.COLOR_BGR2GRAY)
                    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

                    contours_head_patch_con, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours_head_patch_con = return_parent_contours(contours_head_patch_con, hiearchy)

                    imgray = cv2.cvtColor(main_patch_con, cv2.COLOR_BGR2GRAY)
                    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

                    contours_main_patch_con, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours_main_patch_con = return_parent_contours(contours_main_patch_con, hiearchy)

                    _, _, areas_head = find_features_of_contours(contours_head_patch_con)
                    _, _, areas_main = find_features_of_contours(contours_main_patch_con)

                    if np.sum(areas_head) > np.sum(areas_main):
                        img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0][img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0] == 1] = 2
                    else:
                        img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0][img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0] == 2] = 1

                elif y_patch_head_min[i] < y_patch_main_max[j] and y_patch_head_max[i] > y_patch_main_max[j]:
                    y_down = y_patch_main_max[j]
                    y_up = y_patch_head_min[i]

                    patch_intersection = np.zeros(asp.shape)
                    patch_intersection[y_up:y_down, :] = asp[y_up:y_down, :]

                    head_patch_con = (patch_intersection[:, :] == 2) * 1
                    main_patch_con = (patch_intersection[:, :] == 1) * 1
                    head_patch_con = head_patch_con.astype(np.uint8)
                    main_patch_con = main_patch_con.astype(np.uint8)

                    head_patch_con = np.repeat(head_patch_con[:, :, np.newaxis], 3, axis=2)
                    main_patch_con = np.repeat(main_patch_con[:, :, np.newaxis], 3, axis=2)

                    imgray = cv2.cvtColor(head_patch_con, cv2.COLOR_BGR2GRAY)
                    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

                    contours_head_patch_con, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours_head_patch_con = return_parent_contours(contours_head_patch_con, hiearchy)

                    imgray = cv2.cvtColor(main_patch_con, cv2.COLOR_BGR2GRAY)
                    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

                    contours_main_patch_con, hiearchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                    contours_main_patch_con = return_parent_contours(contours_main_patch_con, hiearchy)

                    _, _, areas_head = find_features_of_contours(contours_head_patch_con)
                    _, _, areas_main = find_features_of_contours(contours_main_patch_con)

                    if np.sum(areas_head) > np.sum(areas_main):
                        img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0][img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0] == 1] = 2
                    else:
                        img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0][img_revised_tab[y_up:y_down, int(boxes[ind][0]) : int(boxes[ind][1]), 0] == 2] = 1

                    # print(np.unique(patch_intersection) )
                    ##plt.figure(figsize=(20,20))
                    ##plt.imshow(patch_intersection)
                    ##plt.show()
                else:
                    pass

    return img_revised_tab

def tear_main_texts_on_the_boundaries_of_boxes(img_revised_tab, boxes):
    for i in range(len(boxes)):
        img_revised_tab[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][1] - 10) : int(boxes[i][1]), 0][img_revised_tab[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][1] - 10) : int(boxes[i][1]), 0] == 1] = 0
        img_revised_tab[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][1] - 10) : int(boxes[i][1]), 1][img_revised_tab[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][1] - 10) : int(boxes[i][1]), 1] == 1] = 0
        img_revised_tab[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][1] - 10) : int(boxes[i][1]), 2][img_revised_tab[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][1] - 10) : int(boxes[i][1]), 2] == 1] = 0
    return img_revised_tab

def combine_hor_lines_and_delete_cross_points_and_get_lines_features_back(self, regions_pre_p):
    seperators_closeup = ((regions_pre_p[:, :] == 6)) * 1

    seperators_closeup = seperators_closeup.astype(np.uint8)
    kernel = np.ones((5, 5), np.uint8)

    seperators_closeup = cv2.dilate(seperators_closeup, kernel, iterations=1)
    seperators_closeup = cv2.erode(seperators_closeup, kernel, iterations=1)

    seperators_closeup = cv2.erode(seperators_closeup, kernel, iterations=1)
    seperators_closeup = cv2.dilate(seperators_closeup, kernel, iterations=1)

    if len(seperators_closeup.shape) == 2:
        seperators_closeup_n = np.zeros((seperators_closeup.shape[0], seperators_closeup.shape[1], 3))
        seperators_closeup_n[:, :, 0] = seperators_closeup
        seperators_closeup_n[:, :, 1] = seperators_closeup
        seperators_closeup_n[:, :, 2] = seperators_closeup
    else:
        seperators_closeup_n = seperators_closeup[:, :, :]
    # seperators_closeup=seperators_closeup.astype(np.uint8)
    seperators_closeup_n = seperators_closeup_n.astype(np.uint8)
    imgray = cv2.cvtColor(seperators_closeup_n, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 0, 255, 0)
    contours_lines, hierachy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    slope_lines, dist_x, x_min_main, x_max_main, cy_main, slope_lines_org, y_min_main, y_max_main, cx_main = find_features_of_lines(contours_lines)

    dist_y = np.abs(y_max_main - y_min_main)

    slope_lines_org_hor = slope_lines_org[slope_lines == 0]
    args = np.array(range(len(slope_lines)))
    len_x = seperators_closeup.shape[1] * 0
    len_y = seperators_closeup.shape[0] * 0.01

    args_hor = args[slope_lines == 0]
    dist_x_hor = dist_x[slope_lines == 0]
    dist_y_hor = dist_y[slope_lines == 0]
    x_min_main_hor = x_min_main[slope_lines == 0]
    x_max_main_hor = x_max_main[slope_lines == 0]
    cy_main_hor = cy_main[slope_lines == 0]
    y_min_main_hor = y_min_main[slope_lines == 0]
    y_max_main_hor = y_max_main[slope_lines == 0]

    args_hor = args_hor[dist_x_hor >= len_x]
    x_max_main_hor = x_max_main_hor[dist_x_hor >= len_x]
    x_min_main_hor = x_min_main_hor[dist_x_hor >= len_x]
    cy_main_hor = cy_main_hor[dist_x_hor >= len_x]
    y_min_main_hor = y_min_main_hor[dist_x_hor >= len_x]
    y_max_main_hor = y_max_main_hor[dist_x_hor >= len_x]
    slope_lines_org_hor = slope_lines_org_hor[dist_x_hor >= len_x]
    dist_y_hor = dist_y_hor[dist_x_hor >= len_x]
    dist_x_hor = dist_x_hor[dist_x_hor >= len_x]

    args_ver = args[slope_lines == 1]
    dist_y_ver = dist_y[slope_lines == 1]
    dist_x_ver = dist_x[slope_lines == 1]
    x_min_main_ver = x_min_main[slope_lines == 1]
    x_max_main_ver = x_max_main[slope_lines == 1]
    y_min_main_ver = y_min_main[slope_lines == 1]
    y_max_main_ver = y_max_main[slope_lines == 1]
    cx_main_ver = cx_main[slope_lines == 1]

    args_ver = args_ver[dist_y_ver >= len_y]
    x_max_main_ver = x_max_main_ver[dist_y_ver >= len_y]
    x_min_main_ver = x_min_main_ver[dist_y_ver >= len_y]
    cx_main_ver = cx_main_ver[dist_y_ver >= len_y]
    y_min_main_ver = y_min_main_ver[dist_y_ver >= len_y]
    y_max_main_ver = y_max_main_ver[dist_y_ver >= len_y]
    dist_x_ver = dist_x_ver[dist_y_ver >= len_y]
    dist_y_ver = dist_y_ver[dist_y_ver >= len_y]

    img_p_in_ver = np.zeros(seperators_closeup_n[:, :, 2].shape)
    for jv in range(len(args_ver)):
        img_p_in_ver = cv2.fillPoly(img_p_in_ver, pts=[contours_lines[args_ver[jv]]], color=(1, 1, 1))

    img_in_hor = np.zeros(seperators_closeup_n[:, :, 2].shape)
    for jv in range(len(args_hor)):
        img_p_in_hor = cv2.fillPoly(img_in_hor, pts=[contours_lines[args_hor[jv]]], color=(1, 1, 1))

    all_args_uniq = contours_in_same_horizon(cy_main_hor)
    # print(all_args_uniq,'all_args_uniq')
    if len(all_args_uniq) > 0:
        if type(all_args_uniq[0]) is list:
            contours_new = []
            for dd in range(len(all_args_uniq)):
                merged_all = None
                some_args = args_hor[all_args_uniq[dd]]
                some_cy = cy_main_hor[all_args_uniq[dd]]
                some_x_min = x_min_main_hor[all_args_uniq[dd]]
                some_x_max = x_max_main_hor[all_args_uniq[dd]]

                img_in = np.zeros(seperators_closeup_n[:, :, 2].shape)
                for jv in range(len(some_args)):

                    img_p_in = cv2.fillPoly(img_p_in_hor, pts=[contours_lines[some_args[jv]]], color=(1, 1, 1))
                    img_p_in[int(np.mean(some_cy)) - 5 : int(np.mean(some_cy)) + 5, int(np.min(some_x_min)) : int(np.max(some_x_max))] = 1

        else:
            img_p_in = seperators_closeup
    else:
        img_p_in = seperators_closeup

    sep_ver_hor = img_p_in + img_p_in_ver
    sep_ver_hor_cross = (sep_ver_hor == 2) * 1

    sep_ver_hor_cross = np.repeat(sep_ver_hor_cross[:, :, np.newaxis], 3, axis=2)
    sep_ver_hor_cross = sep_ver_hor_cross.astype(np.uint8)
    imgray = cv2.cvtColor(sep_ver_hor_cross, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 0, 255, 0)
    contours_cross, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cx_cross, cy_cross, _, _, _, _, _ = find_new_features_of_contoures(contours_cross)

    for ii in range(len(cx_cross)):
        sep_ver_hor[int(cy_cross[ii]) - 15 : int(cy_cross[ii]) + 15, int(cx_cross[ii]) + 5 : int(cx_cross[ii]) + 40] = 0
        sep_ver_hor[int(cy_cross[ii]) - 15 : int(cy_cross[ii]) + 15, int(cx_cross[ii]) - 40 : int(cx_cross[ii]) - 4] = 0

    img_p_in[:, :] = sep_ver_hor[:, :]

    if len(img_p_in.shape) == 2:
        seperators_closeup_n = np.zeros((img_p_in.shape[0], img_p_in.shape[1], 3))
        seperators_closeup_n[:, :, 0] = img_p_in
        seperators_closeup_n[:, :, 1] = img_p_in
        seperators_closeup_n[:, :, 2] = img_p_in
    else:
        seperators_closeup_n = img_p_in[:, :, :]
    # seperators_closeup=seperators_closeup.astype(np.uint8)
    seperators_closeup_n = seperators_closeup_n.astype(np.uint8)
    imgray = cv2.cvtColor(seperators_closeup_n, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(imgray, 0, 255, 0)

    contours_lines, hierachy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    slope_lines, dist_x, x_min_main, x_max_main, cy_main, slope_lines_org, y_min_main, y_max_main, cx_main = find_features_of_lines(contours_lines)

    dist_y = np.abs(y_max_main - y_min_main)

    slope_lines_org_hor = slope_lines_org[slope_lines == 0]
    args = np.array(range(len(slope_lines)))
    len_x = seperators_closeup.shape[1] * 0.04
    len_y = seperators_closeup.shape[0] * 0.08

    args_hor = args[slope_lines == 0]
    dist_x_hor = dist_x[slope_lines == 0]
    dist_y_hor = dist_y[slope_lines == 0]
    x_min_main_hor = x_min_main[slope_lines == 0]
    x_max_main_hor = x_max_main[slope_lines == 0]
    cy_main_hor = cy_main[slope_lines == 0]
    y_min_main_hor = y_min_main[slope_lines == 0]
    y_max_main_hor = y_max_main[slope_lines == 0]

    args_hor = args_hor[dist_x_hor >= len_x]
    x_max_main_hor = x_max_main_hor[dist_x_hor >= len_x]
    x_min_main_hor = x_min_main_hor[dist_x_hor >= len_x]
    cy_main_hor = cy_main_hor[dist_x_hor >= len_x]
    y_min_main_hor = y_min_main_hor[dist_x_hor >= len_x]
    y_max_main_hor = y_max_main_hor[dist_x_hor >= len_x]
    slope_lines_org_hor = slope_lines_org_hor[dist_x_hor >= len_x]
    dist_y_hor = dist_y_hor[dist_x_hor >= len_x]
    dist_x_hor = dist_x_hor[dist_x_hor >= len_x]

    args_ver = args[slope_lines == 1]
    dist_y_ver = dist_y[slope_lines == 1]
    dist_x_ver = dist_x[slope_lines == 1]
    x_min_main_ver = x_min_main[slope_lines == 1]
    x_max_main_ver = x_max_main[slope_lines == 1]
    y_min_main_ver = y_min_main[slope_lines == 1]
    y_max_main_ver = y_max_main[slope_lines == 1]
    cx_main_ver = cx_main[slope_lines == 1]

    args_ver = args_ver[dist_y_ver >= len_y]
    x_max_main_ver = x_max_main_ver[dist_y_ver >= len_y]
    x_min_main_ver = x_min_main_ver[dist_y_ver >= len_y]
    cx_main_ver = cx_main_ver[dist_y_ver >= len_y]
    y_min_main_ver = y_min_main_ver[dist_y_ver >= len_y]
    y_max_main_ver = y_max_main_ver[dist_y_ver >= len_y]
    dist_x_ver = dist_x_ver[dist_y_ver >= len_y]
    dist_y_ver = dist_y_ver[dist_y_ver >= len_y]

    matrix_of_lines_ch = np.zeros((len(cy_main_hor) + len(cx_main_ver), 10))

    matrix_of_lines_ch[: len(cy_main_hor), 0] = args_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 0] = args_ver

    matrix_of_lines_ch[len(cy_main_hor) :, 1] = cx_main_ver

    matrix_of_lines_ch[: len(cy_main_hor), 2] = x_min_main_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 2] = x_min_main_ver

    matrix_of_lines_ch[: len(cy_main_hor), 3] = x_max_main_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 3] = x_max_main_ver

    matrix_of_lines_ch[: len(cy_main_hor), 4] = dist_x_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 4] = dist_x_ver

    matrix_of_lines_ch[: len(cy_main_hor), 5] = cy_main_hor

    matrix_of_lines_ch[: len(cy_main_hor), 6] = y_min_main_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 6] = y_min_main_ver

    matrix_of_lines_ch[: len(cy_main_hor), 7] = y_max_main_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 7] = y_max_main_ver

    matrix_of_lines_ch[: len(cy_main_hor), 8] = dist_y_hor
    matrix_of_lines_ch[len(cy_main_hor) :, 8] = dist_y_ver

    matrix_of_lines_ch[len(cy_main_hor) :, 9] = 1

    return matrix_of_lines_ch, seperators_closeup_n

def image_change_background_pixels_to_zero(self, image_page):
    image_back_zero = np.zeros((image_page.shape[0], image_page.shape[1]))
    image_back_zero[:, :] = image_page[:, :, 0]
    image_back_zero[:, :][image_back_zero[:, :] == 0] = -255
    image_back_zero[:, :][image_back_zero[:, :] == 255] = 0
    image_back_zero[:, :][image_back_zero[:, :] == -255] = 255
    return image_back_zero

def return_boxes_of_images_by_order_of_reading_without_seperator(spliter_y_new, image_p_rev, regions_without_seperators, matrix_of_lines_ch, seperators_closeup_n):

    boxes = []

    # here I go through main spliters and i do check whether a vertical seperator there is. If so i am searching for \
    # holes in the text and also finding spliter which covers more than one columns.
    for i in range(len(spliter_y_new) - 1):
        # print(spliter_y_new[i],spliter_y_new[i+1])
        matrix_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 6] > spliter_y_new[i]) & (matrix_of_lines_ch[:, 7] < spliter_y_new[i + 1])]
        # print(len( matrix_new[:,9][matrix_new[:,9]==1] ))

        # print(matrix_new[:,8][matrix_new[:,9]==1],'gaddaaa')

        # check to see is there any vertical seperator to find holes.
        if np.abs(spliter_y_new[i + 1] - spliter_y_new[i]) > 1.0 / 3.0 * regions_without_seperators.shape[0]:  # len( matrix_new[:,9][matrix_new[:,9]==1] )>0 and np.max(matrix_new[:,8][matrix_new[:,9]==1])>=0.1*(np.abs(spliter_y_new[i+1]-spliter_y_new[i] )):

            # org_img_dichte=-gaussian_filter1d(( image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,0]/255.).sum(axis=0) ,30)
            # org_img_dichte=org_img_dichte-np.min(org_img_dichte)
            ##plt.figure(figsize=(20,20))
            ##plt.plot(org_img_dichte)
            ##plt.show()
            ###find_num_col_both_layout_and_org(regions_without_seperators,image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,:],7.)

            num_col, peaks_neg_fin = find_num_col_only_image(image_p_rev[int(spliter_y_new[i]) : int(spliter_y_new[i + 1]), :], multiplier=2.4)

            # num_col, peaks_neg_fin=find_num_col(regions_without_seperators[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:],multiplier=7.0)
            x_min_hor_some = matrix_new[:, 2][(matrix_new[:, 9] == 0)]
            x_max_hor_some = matrix_new[:, 3][(matrix_new[:, 9] == 0)]
            cy_hor_some = matrix_new[:, 5][(matrix_new[:, 9] == 0)]
            arg_org_hor_some = matrix_new[:, 0][(matrix_new[:, 9] == 0)]

            peaks_neg_tot = return_points_with_boundies(peaks_neg_fin, 0, seperators_closeup_n[:, :, 0].shape[1])

            start_index_of_hor, newest_peaks, arg_min_hor_sort, lines_length_dels, lines_indexes_deleted = return_hor_spliter_by_index_for_without_verticals(peaks_neg_tot, x_min_hor_some, x_max_hor_some)

            arg_org_hor_some_sort = arg_org_hor_some[arg_min_hor_sort]

            start_index_of_hor_with_subset = [start_index_of_hor[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]  # start_index_of_hor[lines_length_dels>0]
            arg_min_hor_sort_with_subset = [arg_min_hor_sort[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]
            lines_indexes_deleted_with_subset = [lines_indexes_deleted[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]
            lines_length_dels_with_subset = [lines_length_dels[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]

            arg_org_hor_some_sort_subset = [arg_org_hor_some_sort[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]

            # arg_min_hor_sort_with_subset=arg_min_hor_sort[lines_length_dels>0]
            # lines_indexes_deleted_with_subset=lines_indexes_deleted[lines_length_dels>0]
            # lines_length_dels_with_subset=lines_length_dels[lines_length_dels>0]

            # print(len(arg_min_hor_sort),len(arg_org_hor_some_sort),'vizzzzzz')

            vahid_subset = np.zeros((len(start_index_of_hor_with_subset), len(start_index_of_hor_with_subset))) - 1
            for kkk1 in range(len(start_index_of_hor_with_subset)):

                # print(lines_indexes_deleted,'hiii')
                index_del_sub = np.unique(lines_indexes_deleted_with_subset[kkk1])

                for kkk2 in range(len(start_index_of_hor_with_subset)):

                    if set(lines_indexes_deleted_with_subset[kkk2][0]) < set(lines_indexes_deleted_with_subset[kkk1][0]):
                        vahid_subset[kkk1, kkk2] = kkk1
                    else:
                        pass
                # print(set(lines_indexes_deleted[kkk2][0]), set(lines_indexes_deleted[kkk1][0]))

            # check the len of matrix if it has no length means that there is no spliter at all

            if len(vahid_subset > 0):
                # print('hihoo')

                # find parenets args
                line_int = np.zeros(vahid_subset.shape[0])

                childs_id = []
                arg_child = []
                for li in range(vahid_subset.shape[0]):
                    if np.all(vahid_subset[:, li] == -1):
                        line_int[li] = -1
                    else:
                        line_int[li] = 1

                        # childs_args_in=[ idd for idd in range(vahid_subset.shape[0]) if vahid_subset[idd,li]!=-1]
                        # helpi=[]
                        # for nad in range(len(childs_args_in)):
                        #    helpi.append(arg_min_hor_sort_with_subset[childs_args_in[nad]])

                        arg_child.append(arg_min_hor_sort_with_subset[li])

                arg_parent = [arg_min_hor_sort_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij] == -1]
                start_index_of_hor_parent = [start_index_of_hor_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij] == -1]
                # arg_parent=[lines_indexes_deleted_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij]==-1]
                # arg_parent=[lines_length_dels_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij]==-1]

                # arg_child=[arg_min_hor_sort_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij]!=-1]
                start_index_of_hor_child = [start_index_of_hor_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij] != -1]

                cy_hor_some_sort = cy_hor_some[arg_parent]

                newest_y_spliter_tot = []

                for tj in range(len(newest_peaks) - 1):
                    newest_y_spliter = []
                    newest_y_spliter.append(spliter_y_new[i])
                    if tj in np.unique(start_index_of_hor_parent):
                        cy_help = np.array(cy_hor_some_sort)[np.array(start_index_of_hor_parent) == tj]
                        cy_help_sort = np.sort(cy_help)

                        # print(tj,cy_hor_some_sort,start_index_of_hor,cy_help,'maashhaha')
                        for mj in range(len(cy_help_sort)):
                            newest_y_spliter.append(cy_help_sort[mj])
                    newest_y_spliter.append(spliter_y_new[i + 1])

                    newest_y_spliter_tot.append(newest_y_spliter)

            else:
                line_int = []
                newest_y_spliter_tot = []

                for tj in range(len(newest_peaks) - 1):
                    newest_y_spliter = []
                    newest_y_spliter.append(spliter_y_new[i])

                    newest_y_spliter.append(spliter_y_new[i + 1])

                    newest_y_spliter_tot.append(newest_y_spliter)

            # if line_int is all -1 means that big spliters have no child and we can easily go through
            if np.all(np.array(line_int) == -1):
                for j in range(len(newest_peaks) - 1):
                    newest_y_spliter = newest_y_spliter_tot[j]

                    for n in range(len(newest_y_spliter) - 1):
                        # print(j,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'maaaa')
                        ##plt.imshow(regions_without_seperators[int(newest_y_spliter[n]):int(newest_y_spliter[n+1]),newest_peaks[j]:newest_peaks[j+1]])
                        ##plt.show()

                        # print(matrix_new[:,0][ (matrix_new[:,9]==1 )])
                        for jvt in matrix_new[:, 0][(matrix_new[:, 9] == 1) & (matrix_new[:, 6] > newest_y_spliter[n]) & (matrix_new[:, 7] < newest_y_spliter[n + 1]) & ((matrix_new[:, 1]) < newest_peaks[j + 1]) & ((matrix_new[:, 1]) > newest_peaks[j])]:
                            pass

                            ###plot_contour(regions_without_seperators.shape[0],regions_without_seperators.shape[1], contours_lines[int(jvt)])
                        # print(matrix_of_lines_ch[matrix_of_lines_ch[:,9]==1])
                        matrix_new_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter[n]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter[n + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < newest_peaks[j + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > newest_peaks[j])]
                        # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                        if 1 > 0:  # len( matrix_new_new[:,9][matrix_new_new[:,9]==1] )>0 and np.max(matrix_new_new[:,8][matrix_new_new[:,9]==1])>=0.2*(np.abs(newest_y_spliter[n+1]-newest_y_spliter[n] )):
                            # num_col_sub, peaks_neg_fin_sub=find_num_col(regions_without_seperators[int(newest_y_spliter[n]):int(newest_y_spliter[n+1]),newest_peaks[j]:newest_peaks[j+1]],multiplier=2.3)
                            num_col_sub, peaks_neg_fin_sub = find_num_col_only_image(image_p_rev[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=2.4)
                        else:
                            peaks_neg_fin_sub = []

                        peaks_sub = []
                        peaks_sub.append(newest_peaks[j])

                        for kj in range(len(peaks_neg_fin_sub)):
                            peaks_sub.append(peaks_neg_fin_sub[kj] + newest_peaks[j])

                        peaks_sub.append(newest_peaks[j + 1])

                        # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                        for kh in range(len(peaks_sub) - 1):
                            boxes.append([peaks_sub[kh], peaks_sub[kh + 1], newest_y_spliter[n], newest_y_spliter[n + 1]])

            else:
                for j in range(len(newest_peaks) - 1):
                    newest_y_spliter = newest_y_spliter_tot[j]

                    if j in start_index_of_hor_parent:

                        x_min_ch = x_min_hor_some[arg_child]
                        x_max_ch = x_max_hor_some[arg_child]
                        cy_hor_some_sort_child = cy_hor_some[arg_child]
                        cy_hor_some_sort_child = np.sort(cy_hor_some_sort_child)

                        for n in range(len(newest_y_spliter) - 1):

                            cy_child_in = cy_hor_some_sort_child[(cy_hor_some_sort_child > newest_y_spliter[n]) & (cy_hor_some_sort_child < newest_y_spliter[n + 1])]

                            if len(cy_child_in) > 0:
                                ###num_col_ch, peaks_neg_ch=find_num_col( regions_without_seperators[int(newest_y_spliter[n]):int(newest_y_spliter[n+1]),newest_peaks[j]:newest_peaks[j+1]],multiplier=2.3)

                                num_col_ch, peaks_neg_ch = find_num_col_only_image(image_p_rev[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=2.3)

                                peaks_neg_ch = peaks_neg_ch[:] + newest_peaks[j]

                                peaks_neg_ch_tot = return_points_with_boundies(peaks_neg_ch, newest_peaks[j], newest_peaks[j + 1])

                                ss_in_ch, nst_p_ch, arg_n_ch, lines_l_del_ch, lines_in_del_ch = return_hor_spliter_by_index_for_without_verticals(peaks_neg_ch_tot, x_min_ch, x_max_ch)

                                newest_y_spliter_ch_tot = []

                                for tjj in range(len(nst_p_ch) - 1):
                                    newest_y_spliter_new = []
                                    newest_y_spliter_new.append(newest_y_spliter[n])
                                    if tjj in np.unique(ss_in_ch):

                                        # print(tj,cy_hor_some_sort,start_index_of_hor,cy_help,'maashhaha')
                                        for mjj in range(len(cy_child_in)):
                                            newest_y_spliter_new.append(cy_child_in[mjj])
                                    newest_y_spliter_new.append(newest_y_spliter[n + 1])

                                    newest_y_spliter_ch_tot.append(newest_y_spliter_new)

                                for jn in range(len(nst_p_ch) - 1):
                                    newest_y_spliter_h = newest_y_spliter_ch_tot[jn]

                                    for nd in range(len(newest_y_spliter_h) - 1):

                                        matrix_new_new2 = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter_h[nd]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter_h[nd + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < nst_p_ch[jn + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > nst_p_ch[jn])]
                                        # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                                        if 1 > 0:  # len( matrix_new_new2[:,9][matrix_new_new2[:,9]==1] )>0 and np.max(matrix_new_new2[:,8][matrix_new_new2[:,9]==1])>=0.2*(np.abs(newest_y_spliter_h[nd+1]-newest_y_spliter_h[nd] )):
                                            # num_col_sub_ch, peaks_neg_fin_sub_ch=find_num_col(regions_without_seperators[int(newest_y_spliter_h[nd]):int(newest_y_spliter_h[nd+1]),nst_p_ch[jn]:nst_p_ch[jn+1]],multiplier=2.3)

                                            num_col_sub_ch, peaks_neg_fin_sub_ch = find_num_col_only_image(image_p_rev[int(newest_y_spliter_h[nd]) : int(newest_y_spliter_h[nd + 1]), nst_p_ch[jn] : nst_p_ch[jn + 1]], multiplier=2.3)
                                            # print(peaks_neg_fin_sub_ch,'gada kutullllllll')
                                        else:
                                            peaks_neg_fin_sub_ch = []

                                        peaks_sub_ch = []
                                        peaks_sub_ch.append(nst_p_ch[jn])

                                        for kjj in range(len(peaks_neg_fin_sub_ch)):
                                            peaks_sub_ch.append(peaks_neg_fin_sub_ch[kjj] + nst_p_ch[jn])

                                        peaks_sub_ch.append(nst_p_ch[jn + 1])

                                        # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                                        for khh in range(len(peaks_sub_ch) - 1):
                                            boxes.append([peaks_sub_ch[khh], peaks_sub_ch[khh + 1], newest_y_spliter_h[nd], newest_y_spliter_h[nd + 1]])

                            else:

                                matrix_new_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter[n]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter[n + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < newest_peaks[j + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > newest_peaks[j])]
                                # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                                if 1 > 0:  # len( matrix_new_new[:,9][matrix_new_new[:,9]==1] )>0 and np.max(matrix_new_new[:,8][matrix_new_new[:,9]==1])>=0.2*(np.abs(newest_y_spliter[n+1]-newest_y_spliter[n] )):
                                    ###num_col_sub, peaks_neg_fin_sub=find_num_col(regions_without_seperators[int(newest_y_spliter[n]):int(newest_y_spliter[n+1]),newest_peaks[j]:newest_peaks[j+1]],multiplier=2.3)
                                    num_col_sub, peaks_neg_fin_sub = find_num_col_only_image(image_p_rev[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=2.3)
                                else:
                                    peaks_neg_fin_sub = []

                                peaks_sub = []
                                peaks_sub.append(newest_peaks[j])

                                for kj in range(len(peaks_neg_fin_sub)):
                                    peaks_sub.append(peaks_neg_fin_sub[kj] + newest_peaks[j])

                                peaks_sub.append(newest_peaks[j + 1])

                                # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                                for kh in range(len(peaks_sub) - 1):
                                    boxes.append([peaks_sub[kh], peaks_sub[kh + 1], newest_y_spliter[n], newest_y_spliter[n + 1]])

                    else:
                        for n in range(len(newest_y_spliter) - 1):

                            for jvt in matrix_new[:, 0][(matrix_new[:, 9] == 1) & (matrix_new[:, 6] > newest_y_spliter[n]) & (matrix_new[:, 7] < newest_y_spliter[n + 1]) & ((matrix_new[:, 1]) < newest_peaks[j + 1]) & ((matrix_new[:, 1]) > newest_peaks[j])]:
                                pass

                                # plot_contour(regions_without_seperators.shape[0],regions_without_seperators.shape[1], contours_lines[int(jvt)])
                            # print(matrix_of_lines_ch[matrix_of_lines_ch[:,9]==1])
                            matrix_new_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter[n]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter[n + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < newest_peaks[j + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > newest_peaks[j])]
                            # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                            if 1 > 0:  # len( matrix_new_new[:,9][matrix_new_new[:,9]==1] )>0 and np.max(matrix_new_new[:,8][matrix_new_new[:,9]==1])>=0.2*(np.abs(newest_y_spliter[n+1]-newest_y_spliter[n] )):
                                ###num_col_sub, peaks_neg_fin_sub=find_num_col(regions_without_seperators[int(newest_y_spliter[n]):int(newest_y_spliter[n+1]),newest_peaks[j]:newest_peaks[j+1]],multiplier=5.0)
                                num_col_sub, peaks_neg_fin_sub = find_num_col_only_image(image_p_rev[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=2.3)
                            else:
                                peaks_neg_fin_sub = []

                            peaks_sub = []
                            peaks_sub.append(newest_peaks[j])

                            for kj in range(len(peaks_neg_fin_sub)):
                                peaks_sub.append(peaks_neg_fin_sub[kj] + newest_peaks[j])

                            peaks_sub.append(newest_peaks[j + 1])

                            # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                            for kh in range(len(peaks_sub) - 1):
                                boxes.append([peaks_sub[kh], peaks_sub[kh + 1], newest_y_spliter[n], newest_y_spliter[n + 1]])

        else:
            boxes.append([0, seperators_closeup_n[:, :, 0].shape[1], spliter_y_new[i], spliter_y_new[i + 1]])
    return boxes

def return_region_segmentation_after_implementing_not_head_maintext_parallel(image_regions_eraly_p, boxes):
    image_revised = np.zeros((image_regions_eraly_p.shape[0], image_regions_eraly_p.shape[1]))
    for i in range(len(boxes)):

        image_box = image_regions_eraly_p[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][0]) : int(boxes[i][1])]
        image_box = np.array(image_box)
        # plt.imshow(image_box)
        # plt.show()

        # print(int(boxes[i][2]),int(boxes[i][3]),int(boxes[i][0]),int(boxes[i][1]),'addaa')
        image_box = implent_law_head_main_not_parallel(image_box)
        image_box = implent_law_head_main_not_parallel(image_box)
        image_box = implent_law_head_main_not_parallel(image_box)

        image_revised[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][0]) : int(boxes[i][1])] = image_box[:, :]
    return image_revised

def return_boxes_of_images_by_order_of_reading_2cols(spliter_y_new, regions_without_seperators, matrix_of_lines_ch, seperators_closeup_n):
    boxes = []

    # here I go through main spliters and i do check whether a vertical seperator there is. If so i am searching for \
    # holes in the text and also finding spliter which covers more than one columns.
    for i in range(len(spliter_y_new) - 1):
        # print(spliter_y_new[i],spliter_y_new[i+1])
        matrix_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 6] > spliter_y_new[i]) & (matrix_of_lines_ch[:, 7] < spliter_y_new[i + 1])]
        # print(len( matrix_new[:,9][matrix_new[:,9]==1] ))

        # print(matrix_new[:,8][matrix_new[:,9]==1],'gaddaaa')

        # check to see is there any vertical seperator to find holes.
        if 1 > 0:  # len( matrix_new[:,9][matrix_new[:,9]==1] )>0 and np.max(matrix_new[:,8][matrix_new[:,9]==1])>=0.1*(np.abs(spliter_y_new[i+1]-spliter_y_new[i] )):
            # print(int(spliter_y_new[i]),int(spliter_y_new[i+1]),'burayaaaa galimiirrrrrrrrrrrrrrrrrrrrrrrrrrr')
            # org_img_dichte=-gaussian_filter1d(( image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,0]/255.).sum(axis=0) ,30)
            # org_img_dichte=org_img_dichte-np.min(org_img_dichte)
            ##plt.figure(figsize=(20,20))
            ##plt.plot(org_img_dichte)
            ##plt.show()
            ###find_num_col_both_layout_and_org(regions_without_seperators,image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,:],7.)

            try:
                num_col, peaks_neg_fin = find_num_col(regions_without_seperators[int(spliter_y_new[i]) : int(spliter_y_new[i + 1]), :], multiplier=7.0)

            except:
                peaks_neg_fin = []
                num_col = 0

            peaks_neg_tot = return_points_with_boundies(peaks_neg_fin, 0, seperators_closeup_n[:, :, 0].shape[1])

            for kh in range(len(peaks_neg_tot) - 1):
                boxes.append([peaks_neg_tot[kh], peaks_neg_tot[kh + 1], spliter_y_new[i], spliter_y_new[i + 1]])

        else:
            boxes.append([0, seperators_closeup_n[:, :, 0].shape[1], spliter_y_new[i], spliter_y_new[i + 1]])

    return boxes

def return_boxes_of_images_by_order_of_reading(spliter_y_new, regions_without_seperators, matrix_of_lines_ch, seperators_closeup_n):
    boxes = []

    # here I go through main spliters and i do check whether a vertical seperator there is. If so i am searching for \
    # holes in the text and also finding spliter which covers more than one columns.
    for i in range(len(spliter_y_new) - 1):
        # print(spliter_y_new[i],spliter_y_new[i+1])
        matrix_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 6] > spliter_y_new[i]) & (matrix_of_lines_ch[:, 7] < spliter_y_new[i + 1])]
        # print(len( matrix_new[:,9][matrix_new[:,9]==1] ))

        # print(matrix_new[:,8][matrix_new[:,9]==1],'gaddaaa')

        # check to see is there any vertical seperator to find holes.
        if len(matrix_new[:, 9][matrix_new[:, 9] == 1]) > 0 and np.max(matrix_new[:, 8][matrix_new[:, 9] == 1]) >= 0.1 * (np.abs(spliter_y_new[i + 1] - spliter_y_new[i])):

            # org_img_dichte=-gaussian_filter1d(( image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,0]/255.).sum(axis=0) ,30)
            # org_img_dichte=org_img_dichte-np.min(org_img_dichte)
            ##plt.figure(figsize=(20,20))
            ##plt.plot(org_img_dichte)
            ##plt.show()
            ###find_num_col_both_layout_and_org(regions_without_seperators,image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,:],7.)

            num_col, peaks_neg_fin = find_num_col(regions_without_seperators[int(spliter_y_new[i]) : int(spliter_y_new[i + 1]), :], multiplier=7.0)

            # num_col, peaks_neg_fin=find_num_col(regions_without_seperators[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:],multiplier=7.0)
            x_min_hor_some = matrix_new[:, 2][(matrix_new[:, 9] == 0)]
            x_max_hor_some = matrix_new[:, 3][(matrix_new[:, 9] == 0)]
            cy_hor_some = matrix_new[:, 5][(matrix_new[:, 9] == 0)]
            arg_org_hor_some = matrix_new[:, 0][(matrix_new[:, 9] == 0)]

            peaks_neg_tot = return_points_with_boundies(peaks_neg_fin, 0, seperators_closeup_n[:, :, 0].shape[1])

            start_index_of_hor, newest_peaks, arg_min_hor_sort, lines_length_dels, lines_indexes_deleted = return_hor_spliter_by_index(peaks_neg_tot, x_min_hor_some, x_max_hor_some)

            arg_org_hor_some_sort = arg_org_hor_some[arg_min_hor_sort]

            start_index_of_hor_with_subset = [start_index_of_hor[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]  # start_index_of_hor[lines_length_dels>0]
            arg_min_hor_sort_with_subset = [arg_min_hor_sort[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]
            lines_indexes_deleted_with_subset = [lines_indexes_deleted[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]
            lines_length_dels_with_subset = [lines_length_dels[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]

            arg_org_hor_some_sort_subset = [arg_org_hor_some_sort[vij] for vij in range(len(start_index_of_hor)) if lines_length_dels[vij] > 0]

            # arg_min_hor_sort_with_subset=arg_min_hor_sort[lines_length_dels>0]
            # lines_indexes_deleted_with_subset=lines_indexes_deleted[lines_length_dels>0]
            # lines_length_dels_with_subset=lines_length_dels[lines_length_dels>0]

            vahid_subset = np.zeros((len(start_index_of_hor_with_subset), len(start_index_of_hor_with_subset))) - 1
            for kkk1 in range(len(start_index_of_hor_with_subset)):

                index_del_sub = np.unique(lines_indexes_deleted_with_subset[kkk1])

                for kkk2 in range(len(start_index_of_hor_with_subset)):

                    if set(lines_indexes_deleted_with_subset[kkk2][0]) < set(lines_indexes_deleted_with_subset[kkk1][0]):
                        vahid_subset[kkk1, kkk2] = kkk1
                    else:
                        pass
                # print(set(lines_indexes_deleted[kkk2][0]), set(lines_indexes_deleted[kkk1][0]))

            # print(vahid_subset,'zartt222')

            # check the len of matrix if it has no length means that there is no spliter at all

            if len(vahid_subset > 0):
                # print('hihoo')

                # find parenets args
                line_int = np.zeros(vahid_subset.shape[0])

                childs_id = []
                arg_child = []
                for li in range(vahid_subset.shape[0]):
                    # print(vahid_subset[:,li])
                    if np.all(vahid_subset[:, li] == -1):
                        line_int[li] = -1
                    else:
                        line_int[li] = 1

                        # childs_args_in=[ idd for idd in range(vahid_subset.shape[0]) if vahid_subset[idd,li]!=-1]
                        # helpi=[]
                        # for nad in range(len(childs_args_in)):
                        #    helpi.append(arg_min_hor_sort_with_subset[childs_args_in[nad]])

                        arg_child.append(arg_min_hor_sort_with_subset[li])

                # line_int=vahid_subset[0,:]

                # print(arg_child,line_int[0],'zartt33333')
                arg_parent = [arg_min_hor_sort_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij] == -1]
                start_index_of_hor_parent = [start_index_of_hor_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij] == -1]
                # arg_parent=[lines_indexes_deleted_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij]==-1]
                # arg_parent=[lines_length_dels_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij]==-1]

                # arg_child=[arg_min_hor_sort_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij]!=-1]
                start_index_of_hor_child = [start_index_of_hor_with_subset[vij] for vij in range(len(arg_min_hor_sort_with_subset)) if line_int[vij] != -1]

                cy_hor_some_sort = cy_hor_some[arg_parent]

                # print(start_index_of_hor, lines_length_dels ,lines_indexes_deleted,'zartt')

                # args_indexes=np.array(range(len(start_index_of_hor) ))

                newest_y_spliter_tot = []

                for tj in range(len(newest_peaks) - 1):
                    newest_y_spliter = []
                    newest_y_spliter.append(spliter_y_new[i])
                    if tj in np.unique(start_index_of_hor_parent):
                        ##print(cy_hor_some_sort)
                        cy_help = np.array(cy_hor_some_sort)[np.array(start_index_of_hor_parent) == tj]
                        cy_help_sort = np.sort(cy_help)

                        # print(tj,cy_hor_some_sort,start_index_of_hor,cy_help,'maashhaha')
                        for mj in range(len(cy_help_sort)):
                            newest_y_spliter.append(cy_help_sort[mj])
                    newest_y_spliter.append(spliter_y_new[i + 1])

                    newest_y_spliter_tot.append(newest_y_spliter)

            else:
                line_int = []
                newest_y_spliter_tot = []

                for tj in range(len(newest_peaks) - 1):
                    newest_y_spliter = []
                    newest_y_spliter.append(spliter_y_new[i])

                    newest_y_spliter.append(spliter_y_new[i + 1])

                    newest_y_spliter_tot.append(newest_y_spliter)

            # if line_int is all -1 means that big spliters have no child and we can easily go through
            if np.all(np.array(line_int) == -1):
                for j in range(len(newest_peaks) - 1):
                    newest_y_spliter = newest_y_spliter_tot[j]

                    for n in range(len(newest_y_spliter) - 1):
                        # print(j,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'maaaa')
                        ##plt.imshow(regions_without_seperators[int(newest_y_spliter[n]):int(newest_y_spliter[n+1]),newest_peaks[j]:newest_peaks[j+1]])
                        ##plt.show()

                        # print(matrix_new[:,0][ (matrix_new[:,9]==1 )])
                        for jvt in matrix_new[:, 0][(matrix_new[:, 9] == 1) & (matrix_new[:, 6] > newest_y_spliter[n]) & (matrix_new[:, 7] < newest_y_spliter[n + 1]) & ((matrix_new[:, 1]) < newest_peaks[j + 1]) & ((matrix_new[:, 1]) > newest_peaks[j])]:
                            pass

                            ###plot_contour(regions_without_seperators.shape[0],regions_without_seperators.shape[1], contours_lines[int(jvt)])
                        # print(matrix_of_lines_ch[matrix_of_lines_ch[:,9]==1])
                        matrix_new_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter[n]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter[n + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < newest_peaks[j + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > newest_peaks[j])]
                        # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                        if len(matrix_new_new[:, 9][matrix_new_new[:, 9] == 1]) > 0 and np.max(matrix_new_new[:, 8][matrix_new_new[:, 9] == 1]) >= 0.2 * (np.abs(newest_y_spliter[n + 1] - newest_y_spliter[n])):
                            num_col_sub, peaks_neg_fin_sub = find_num_col(regions_without_seperators[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=5.0)
                        else:
                            peaks_neg_fin_sub = []

                        peaks_sub = []
                        peaks_sub.append(newest_peaks[j])

                        for kj in range(len(peaks_neg_fin_sub)):
                            peaks_sub.append(peaks_neg_fin_sub[kj] + newest_peaks[j])

                        peaks_sub.append(newest_peaks[j + 1])

                        # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                        for kh in range(len(peaks_sub) - 1):
                            boxes.append([peaks_sub[kh], peaks_sub[kh + 1], newest_y_spliter[n], newest_y_spliter[n + 1]])

            else:
                for j in range(len(newest_peaks) - 1):
                    newest_y_spliter = newest_y_spliter_tot[j]

                    if j in start_index_of_hor_parent:

                        x_min_ch = x_min_hor_some[arg_child]
                        x_max_ch = x_max_hor_some[arg_child]
                        cy_hor_some_sort_child = cy_hor_some[arg_child]
                        cy_hor_some_sort_child = np.sort(cy_hor_some_sort_child)

                        # print(cy_hor_some_sort_child,'ychilds')

                        for n in range(len(newest_y_spliter) - 1):

                            cy_child_in = cy_hor_some_sort_child[(cy_hor_some_sort_child > newest_y_spliter[n]) & (cy_hor_some_sort_child < newest_y_spliter[n + 1])]

                            if len(cy_child_in) > 0:
                                num_col_ch, peaks_neg_ch = find_num_col(regions_without_seperators[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=5.0)
                                # print(peaks_neg_ch,'mizzzz')
                                # peaks_neg_ch=[]
                                # for djh in range(len(peaks_neg_ch)):
                                #    peaks_neg_ch.append( peaks_neg_ch[djh]+newest_peaks[j] )

                                peaks_neg_ch_tot = return_points_with_boundies(peaks_neg_ch, newest_peaks[j], newest_peaks[j + 1])

                                ss_in_ch, nst_p_ch, arg_n_ch, lines_l_del_ch, lines_in_del_ch = return_hor_spliter_by_index(peaks_neg_ch_tot, x_min_ch, x_max_ch)

                                newest_y_spliter_ch_tot = []

                                for tjj in range(len(nst_p_ch) - 1):
                                    newest_y_spliter_new = []
                                    newest_y_spliter_new.append(newest_y_spliter[n])
                                    if tjj in np.unique(ss_in_ch):

                                        # print(tj,cy_hor_some_sort,start_index_of_hor,cy_help,'maashhaha')
                                        for mjj in range(len(cy_child_in)):
                                            newest_y_spliter_new.append(cy_child_in[mjj])
                                    newest_y_spliter_new.append(newest_y_spliter[n + 1])

                                    newest_y_spliter_ch_tot.append(newest_y_spliter_new)

                                for jn in range(len(nst_p_ch) - 1):
                                    newest_y_spliter_h = newest_y_spliter_ch_tot[jn]

                                    for nd in range(len(newest_y_spliter_h) - 1):

                                        matrix_new_new2 = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter_h[nd]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter_h[nd + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < nst_p_ch[jn + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > nst_p_ch[jn])]
                                        # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                                        if len(matrix_new_new2[:, 9][matrix_new_new2[:, 9] == 1]) > 0 and np.max(matrix_new_new2[:, 8][matrix_new_new2[:, 9] == 1]) >= 0.2 * (np.abs(newest_y_spliter_h[nd + 1] - newest_y_spliter_h[nd])):
                                            num_col_sub_ch, peaks_neg_fin_sub_ch = find_num_col(regions_without_seperators[int(newest_y_spliter_h[nd]) : int(newest_y_spliter_h[nd + 1]), nst_p_ch[jn] : nst_p_ch[jn + 1]], multiplier=5.0)

                                        else:
                                            peaks_neg_fin_sub_ch = []

                                        peaks_sub_ch = []
                                        peaks_sub_ch.append(nst_p_ch[jn])

                                        for kjj in range(len(peaks_neg_fin_sub_ch)):
                                            peaks_sub_ch.append(peaks_neg_fin_sub_ch[kjj] + nst_p_ch[jn])

                                        peaks_sub_ch.append(nst_p_ch[jn + 1])

                                        # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                                        for khh in range(len(peaks_sub_ch) - 1):
                                            boxes.append([peaks_sub_ch[khh], peaks_sub_ch[khh + 1], newest_y_spliter_h[nd], newest_y_spliter_h[nd + 1]])

                            else:

                                matrix_new_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter[n]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter[n + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < newest_peaks[j + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > newest_peaks[j])]
                                # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                                if len(matrix_new_new[:, 9][matrix_new_new[:, 9] == 1]) > 0 and np.max(matrix_new_new[:, 8][matrix_new_new[:, 9] == 1]) >= 0.2 * (np.abs(newest_y_spliter[n + 1] - newest_y_spliter[n])):
                                    num_col_sub, peaks_neg_fin_sub = find_num_col(regions_without_seperators[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=5.0)
                                else:
                                    peaks_neg_fin_sub = []

                                peaks_sub = []
                                peaks_sub.append(newest_peaks[j])

                                for kj in range(len(peaks_neg_fin_sub)):
                                    peaks_sub.append(peaks_neg_fin_sub[kj] + newest_peaks[j])

                                peaks_sub.append(newest_peaks[j + 1])

                                # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                                for kh in range(len(peaks_sub) - 1):
                                    boxes.append([peaks_sub[kh], peaks_sub[kh + 1], newest_y_spliter[n], newest_y_spliter[n + 1]])

                    else:
                        for n in range(len(newest_y_spliter) - 1):

                            # plot_contour(regions_without_seperators.shape[0],regions_without_seperators.shape[1], contours_lines[int(jvt)])
                            # print(matrix_of_lines_ch[matrix_of_lines_ch[:,9]==1])
                            matrix_new_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 9] == 1) & (matrix_of_lines_ch[:, 6] > newest_y_spliter[n]) & (matrix_of_lines_ch[:, 7] < newest_y_spliter[n + 1]) & ((matrix_of_lines_ch[:, 1] + 500) < newest_peaks[j + 1]) & ((matrix_of_lines_ch[:, 1] - 500) > newest_peaks[j])]
                            # print(matrix_new_new,newest_y_spliter[n],newest_y_spliter[n+1],newest_peaks[j],newest_peaks[j+1],'gada')
                            if len(matrix_new_new[:, 9][matrix_new_new[:, 9] == 1]) > 0 and np.max(matrix_new_new[:, 8][matrix_new_new[:, 9] == 1]) >= 0.2 * (np.abs(newest_y_spliter[n + 1] - newest_y_spliter[n])):
                                num_col_sub, peaks_neg_fin_sub = find_num_col(regions_without_seperators[int(newest_y_spliter[n]) : int(newest_y_spliter[n + 1]), newest_peaks[j] : newest_peaks[j + 1]], multiplier=5.0)
                            else:
                                peaks_neg_fin_sub = []

                            peaks_sub = []
                            peaks_sub.append(newest_peaks[j])

                            for kj in range(len(peaks_neg_fin_sub)):
                                peaks_sub.append(peaks_neg_fin_sub[kj] + newest_peaks[j])

                            peaks_sub.append(newest_peaks[j + 1])

                            # peaks_sub=return_points_with_boundies(peaks_neg_fin_sub+newest_peaks[j],newest_peaks[j], newest_peaks[j+1])

                            for kh in range(len(peaks_sub) - 1):
                                boxes.append([peaks_sub[kh], peaks_sub[kh + 1], newest_y_spliter[n], newest_y_spliter[n + 1]])

        else:
            boxes.append([0, seperators_closeup_n[:, :, 0].shape[1], spliter_y_new[i], spliter_y_new[i + 1]])

    return boxes

def return_boxes_of_images_by_order_of_reading_without_seperators_2cols(spliter_y_new, image_p_rev, regions_without_seperators, matrix_of_lines_ch, seperators_closeup_n):

    boxes = []

    # here I go through main spliters and i do check whether a vertical seperator there is. If so i am searching for \
    # holes in the text and also finding spliter which covers more than one columns.
    for i in range(len(spliter_y_new) - 1):
        # print(spliter_y_new[i],spliter_y_new[i+1])
        matrix_new = matrix_of_lines_ch[:, :][(matrix_of_lines_ch[:, 6] > spliter_y_new[i]) & (matrix_of_lines_ch[:, 7] < spliter_y_new[i + 1])]
        # print(len( matrix_new[:,9][matrix_new[:,9]==1] ))

        # print(matrix_new[:,8][matrix_new[:,9]==1],'gaddaaa')

        # check to see is there any vertical seperator to find holes.
        if np.abs(spliter_y_new[i + 1] - spliter_y_new[i]) > 1.0 / 3.0 * regions_without_seperators.shape[0]:  # len( matrix_new[:,9][matrix_new[:,9]==1] )>0 and np.max(matrix_new[:,8][matrix_new[:,9]==1])>=0.1*(np.abs(spliter_y_new[i+1]-spliter_y_new[i] )):

            # org_img_dichte=-gaussian_filter1d(( image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,0]/255.).sum(axis=0) ,30)
            # org_img_dichte=org_img_dichte-np.min(org_img_dichte)
            ##plt.figure(figsize=(20,20))
            ##plt.plot(org_img_dichte)
            ##plt.show()
            ###find_num_col_both_layout_and_org(regions_without_seperators,image_page[int(spliter_y_new[i]):int(spliter_y_new[i+1]),:,:],7.)

            try:
                num_col, peaks_neg_fin = find_num_col_only_image(image_p_rev[int(spliter_y_new[i]) : int(spliter_y_new[i + 1]), :], multiplier=2.4)
            except:
                peaks_neg_fin = []
                num_col = 0

            peaks_neg_tot = return_points_with_boundies(peaks_neg_fin, 0, seperators_closeup_n[:, :, 0].shape[1])

            for kh in range(len(peaks_neg_tot) - 1):
                boxes.append([peaks_neg_tot[kh], peaks_neg_tot[kh + 1], spliter_y_new[i], spliter_y_new[i + 1]])
        else:
            boxes.append([0, seperators_closeup_n[:, :, 0].shape[1], spliter_y_new[i], spliter_y_new[i + 1]])

    return boxes

def add_tables_heuristic_to_layout(image_regions_eraly_p, boxes, slope_mean_hor, spliter_y, peaks_neg_tot, image_revised):

    image_revised_1 = delete_seperator_around(spliter_y, peaks_neg_tot, image_revised)
    img_comm_e = np.zeros(image_revised_1.shape)
    img_comm = np.repeat(img_comm_e[:, :, np.newaxis], 3, axis=2)

    for indiv in np.unique(image_revised_1):

        # print(indiv,'indd')
        image_col = (image_revised_1 == indiv) * 255
        img_comm_in = np.repeat(image_col[:, :, np.newaxis], 3, axis=2)
        img_comm_in = img_comm_in.astype(np.uint8)

        imgray = cv2.cvtColor(img_comm_in, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(imgray, 0, 255, 0)

        contours, hirarchy = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        main_contours = filter_contours_area_of_image_tables(thresh, contours, hirarchy, max_area=1, min_area=0.0001)

        img_comm = cv2.fillPoly(img_comm, pts=main_contours, color=(indiv, indiv, indiv))
        ###img_comm_in=cv2.fillPoly(img_comm, pts =interior_contours, color=(0,0,0))

        # img_comm=np.repeat(img_comm[:, :, np.newaxis], 3, axis=2)
        img_comm = img_comm.astype(np.uint8)

    if not isNaN(slope_mean_hor):
        image_revised_last = np.zeros((image_regions_eraly_p.shape[0], image_regions_eraly_p.shape[1], 3))
        for i in range(len(boxes)):

            image_box = img_comm[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][0]) : int(boxes[i][1]), :]

            image_box_tabels_1 = (image_box[:, :, 0] == 7) * 1

            contours_tab, _ = return_contours_of_image(image_box_tabels_1)

            contours_tab = filter_contours_area_of_image_tables(image_box_tabels_1, contours_tab, _, 1, 0.001)

            image_box_tabels_1 = (image_box[:, :, 0] == 6) * 1

            image_box_tabels_and_m_text = ((image_box[:, :, 0] == 7) | (image_box[:, :, 0] == 1)) * 1
            image_box_tabels_and_m_text = image_box_tabels_and_m_text.astype(np.uint8)

            image_box_tabels_1 = image_box_tabels_1.astype(np.uint8)
            image_box_tabels_1 = cv2.dilate(image_box_tabels_1, self.kernel, iterations=5)

            contours_table_m_text, _ = return_contours_of_image(image_box_tabels_and_m_text)

            image_box_tabels = np.repeat(image_box_tabels_1[:, :, np.newaxis], 3, axis=2)

            image_box_tabels = image_box_tabels.astype(np.uint8)
            imgray = cv2.cvtColor(image_box_tabels, cv2.COLOR_BGR2GRAY)
            ret, thresh = cv2.threshold(imgray, 0, 255, 0)

            contours_line, hierachy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            y_min_main_line, y_max_main_line, _ = find_features_of_contours(contours_line)
            # _,_,y_min_main_line ,y_max_main_line,x_min_main_line,x_max_main_line=find_new_features_of_contoures(contours_line)
            y_min_main_tab, y_max_main_tab, _ = find_features_of_contours(contours_tab)

            cx_tab_m_text, cy_tab_m_text, x_min_tab_m_text, x_max_tab_m_text, y_min_tab_m_text, y_max_tab_m_text = find_new_features_of_contoures(contours_table_m_text)
            cx_tabl, cy_tabl, x_min_tabl, x_max_tabl, y_min_tabl, y_max_tabl, _ = find_new_features_of_contoures(contours_tab)

            if len(y_min_main_tab) > 0:
                y_down_tabs = []
                y_up_tabs = []

                for i_t in range(len(y_min_main_tab)):
                    y_down_tab = []
                    y_up_tab = []
                    for i_l in range(len(y_min_main_line)):
                        if y_min_main_tab[i_t] > y_min_main_line[i_l] and y_max_main_tab[i_t] > y_min_main_line[i_l] and y_min_main_tab[i_t] > y_max_main_line[i_l] and y_max_main_tab[i_t] > y_min_main_line[i_l]:
                            pass
                        elif y_min_main_tab[i_t] < y_max_main_line[i_l] and y_max_main_tab[i_t] < y_max_main_line[i_l] and y_max_main_tab[i_t] < y_min_main_line[i_l] and y_min_main_tab[i_t] < y_min_main_line[i_l]:
                            pass
                        elif np.abs(y_max_main_line[i_l] - y_min_main_line[i_l]) < 100:
                            pass

                        else:
                            y_up_tab.append(np.min([y_min_main_line[i_l], y_min_main_tab[i_t]]))
                            y_down_tab.append(np.max([y_max_main_line[i_l], y_max_main_tab[i_t]]))

                    if len(y_up_tab) == 0:
                        for v_n in range(len(cx_tab_m_text)):
                            if cx_tabl[i_t] <= x_max_tab_m_text[v_n] and cx_tabl[i_t] >= x_min_tab_m_text[v_n] and cy_tabl[i_t] <= y_max_tab_m_text[v_n] and cy_tabl[i_t] >= y_min_tab_m_text[v_n] and cx_tabl[i_t] != cx_tab_m_text[v_n] and cy_tabl[i_t] != cy_tab_m_text[v_n]:
                                y_up_tabs.append(y_min_tab_m_text[v_n])
                                y_down_tabs.append(y_max_tab_m_text[v_n])
                        # y_up_tabs.append(y_min_main_tab[i_t])
                        # y_down_tabs.append(y_max_main_tab[i_t])
                    else:
                        y_up_tabs.append(np.min(y_up_tab))
                        y_down_tabs.append(np.max(y_down_tab))

            else:
                y_down_tabs = []
                y_up_tabs = []
                pass

            for ii in range(len(y_up_tabs)):
                image_box[y_up_tabs[ii] : y_down_tabs[ii], :, 0] = 7

            image_revised_last[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][0]) : int(boxes[i][1]), :] = image_box[:, :, :]

    else:
        for i in range(len(boxes)):

            image_box = img_comm[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][0]) : int(boxes[i][1]), :]
            image_revised_last[int(boxes[i][2]) : int(boxes[i][3]), int(boxes[i][0]) : int(boxes[i][1]), :] = image_box[:, :, :]

            ##plt.figure(figsize=(20,20))
            ##plt.imshow(image_box[:,:,0])
            ##plt.show()
    return image_revised_last

