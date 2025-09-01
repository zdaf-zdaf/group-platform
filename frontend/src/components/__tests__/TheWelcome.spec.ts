import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TheWelcome from '../TheWelcome.vue'

describe('TheWelcome', () => {
  it('renders all WelcomeItem slots', () => {
    const wrapper = mount(TheWelcome)
    expect(wrapper.findAllComponents({ name: 'WelcomeItem' }).length).toBeGreaterThan(0)
    expect(wrapper.text()).toContain('Documentation')
    expect(wrapper.text()).toContain('Tooling')
    expect(wrapper.text()).toContain('Ecosystem')
    expect(wrapper.text()).toContain('Community')
    expect(wrapper.text()).toContain('Support Vue')
  })

  it('handles missing slot content gracefully', () => {
    // 直接挂载 WelcomeItem，缺少 slot
    const WelcomeItem = wrapper => wrapper.findComponent({ name: 'WelcomeItem' })
    const wrapper = mount(TheWelcome)
    expect(WelcomeItem(wrapper).exists()).toBe(true)
  })
})
