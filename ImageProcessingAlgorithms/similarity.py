import cv2
from skimage.metrics import structural_similarity as ssim
def orb_feature_compare(imageA, imageB):
    # Convert to grayscale
    imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Find the keypoints and descriptors with ORB
    kpA, desA = orb.detectAndCompute(imageA, None)
    kpB, desB = orb.detectAndCompute(imageB, None)

    # Match descriptors
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desA, desB)
    
    # Sort matches by distance
    matches = sorted(matches, key=lambda x: x.distance)
    
    return len(matches), matches
def compare_histograms(imageA, imageB, method='correlation'):
    # Convert images to HSV color space for better comparison
    imageA = cv2.cvtColor(imageA, cv2.COLOR_BGR2HSV)
    imageB = cv2.cvtColor(imageB, cv2.COLOR_BGR2HSV)

    # Calculate histograms
    histA = cv2.calcHist([imageA], [0, 1], None, [50, 60], [0, 180, 0, 256])
    histB = cv2.calcHist([imageB], [0, 1], None, [50, 60], [0, 180, 0, 256])

    # Normalize histograms
    cv2.normalize(histA, histA, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    cv2.normalize(histB, histB, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    # Use correlation or other methods
    methods = {
        'correlation': cv2.HISTCMP_CORREL,
        'chi-square': cv2.HISTCMP_CHISQR,
        'bhattacharyya': cv2.HISTCMP_BHATTACHARYYA
    }

    comparison = cv2.compareHist(histA, histB, methods[method])
    return comparison
def compare_ssim(imageA, imageB):
    if imageA is None or imageB is None:
        raise ValueError("One or both images are None")

    # Convert to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # Resize if needed
    if grayA.shape != grayB.shape:
        grayB = cv2.resize(grayB, (grayA.shape[1], grayA.shape[0]))

    h, w = grayA.shape

    # Safe window size
    win_size = min(7, h, w)
    if win_size % 2 == 0:
        win_size -= 1

    if win_size < 3:
        raise ValueError("Images too small for SSIM")

    score, _ = ssim(grayA, grayB, win_size=win_size, full=True)
    return score

#=======================================================#
#INPUT#
# Load images
imageA = cv2.imread('1.jpg') #PREVIOUS DAY IMAGE AS REFERENCE
imageB = cv2.imread('2.jpg')
#=======================================================#

# Compare features using ORB
matches_count, matches = orb_feature_compare(imageA, imageB)
print(f"Number of Matches: {matches_count}")

# Compare histograms using correlation
hist_score = compare_histograms(imageA, imageB, method='correlation')
print(f"Histogram Comparison Score (Correlation): {hist_score}")

# Compute SSIM
ssim_score = compare_ssim(imageA, imageB)
print(f"SSIM Score: {ssim_score}")

#=======================================================#
#OUTPUT
if matches_count >300 & hist_score >0.9 & ssim_score>0.9:
    output = True
else:
    output = False
#=======================================================#