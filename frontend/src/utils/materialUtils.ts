// 材料管理本地工具函数
export function addMaterial(store: any[], material: any) {
  if (store.some(m => m.id === material.id)) {
    throw new Error('Material already exists')
  }
  store.push(material)
}

export function removeMaterial(store: any[], id: number) {
  const idx = store.findIndex(m => m.id === id)
  if (idx === -1) throw new Error('Material not found')
  store.splice(idx, 1)
}

export function updateMaterial(store: any[], id: number, data: Partial<any>) {
  const m = store.find(m => m.id === id)
  if (!m) throw new Error('Material not found')
  Object.assign(m, data)
}

export function getMaterial(store: any[], id: number) {
  return store.find(m => m.id === id) || null
}
