import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import HelloWorld from '../HelloWorld.vue'

describe('HelloWorld', () => {
  it('renders properly', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'Hello Vitest' } })
    expect(wrapper.text()).toContain('Hello Vitest')
  })

  it('renders empty h1 if msg is empty', () => {
    const wrapper = mount(HelloWorld, { props: { msg: '' } })
    expect(wrapper.find('h1').text()).toBe('')
    expect(wrapper.text()).toContain('You’ve successfully created a project')
  })
})
