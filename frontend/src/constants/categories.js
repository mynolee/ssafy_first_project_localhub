export const POST_CATEGORIES = [
  { value: '', label: '전체' },
  { value: 'TOURIST', label: '관광지' },
  { value: 'RESTAURANT', label: '맛집' },
  { value: 'FESTIVAL', label: '축제' },
  { value: 'CULTURE', label: '문화시설' },
]

export const PLACE_CATEGORIES = [
  ...POST_CATEGORIES,
  { value: 'COURSE', label: '여행코스' },
  { value: 'LEISURE', label: '레포츠' },
  { value: 'SHOPPING', label: '쇼핑' },
  { value: 'ACCOMMODATION', label: '숙박' },
]

export const CATEGORY_LABELS = Object.fromEntries(
  PLACE_CATEGORIES.filter(({ value }) => value).map(({ value, label }) => [value, label]),
)

export const REGIONS = [
  { value: '', label: '전국' },
  { value: 'SEOUL', label: '서울' },
  { value: 'DAEJEON_CHUNGCHEONG', label: '대전·충청' },
  { value: 'GUMI_GYEONGBUK', label: '구미·경북' },
  { value: 'GWANGJU_JEOLLA', label: '광주·전라' },
  { value: 'BUSAN', label: '부산' },
]

export const REGION_LABELS = Object.fromEntries(
  REGIONS.filter(({ value }) => value).map(({ value, label }) => [value, label]),
)
