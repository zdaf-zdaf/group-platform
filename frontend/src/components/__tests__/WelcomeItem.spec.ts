import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import WelcomeItem from '../WelcomeItem.vue'

describe('WelcomeItem', () => {
  it('renders slot content', () => {
    const wrapper = mount(WelcomeItem, {
      slots: {
        icon: '<span>icon</span>',
        heading: '<span>heading</span>',
        default: '<span>default</span>'
      }
    })
    expect(wrapper.html()).toContain('icon')
    expect(wrapper.html()).toContain('heading')
    expect(wrapper.html()).toContain('default')
  })

  it('renders gracefully with missing slots', () => {
    const wrapper = mount(WelcomeItem)
    expect(wrapper.exists()).toBe(true)
    // 没有slot时内容为空但不报错
    expect(wrapper.text()).toBe('')
  })
})
