export const POST_CATEGORIES = [
  { value: '', label: '전체' },
  { value: 'TOURIST', label: '관광지' },
  { value: 'RESTAURANT', label: '맛집' },
  { value: 'FESTIVAL', label: '축제' },
]

export const PLACE_CATEGORIES = [
  ...POST_CATEGORIES,
  { value: 'CULTURE', label: '문화' },
  { value: 'SHOPPING', label: '쇼핑' },
  { value: 'ACCOMMODATION', label: '숙박' },
]

export const CATEGORY_LABELS = Object.fromEntries(
  PLACE_CATEGORIES.filter(({ value }) => value).map(({ value, label }) => [value, label]),
)

