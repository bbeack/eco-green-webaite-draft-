// Shared behaviour for the Rootstock Framer components.
//
// The static site drives its animations from assets/js/site.js, which binds to
// the whole document on load. Inside Framer a component owns only its own
// subtree and can mount or unmount at any time, so the same behaviour is
// expressed here as hooks scoped to a ref.
//
// Components import everything from this one file, so a Framer project only
// needs two shared code files rather than one per concern.

import { useEffect, useRef, useState } from "react"
import type { FormEvent, RefObject } from "react"
import { useRootstock, assets, designSystemCss } from "./RootstockDesignSystem"
import type { Theme } from "./RootstockDesignSystem"

export { useRootstock, assets, designSystemCss }
export type { Theme }

export function useReducedMotion(): boolean {
    const [reduced, setReduced] = useState(false)
    useEffect(() => {
        const mq = window.matchMedia("(prefers-reduced-motion: reduce)")
        const update = () => setReduced(mq.matches)
        update()
        mq.addEventListener("change", update)
        return () => mq.removeEventListener("change", update)
    }, [])
    return reduced
}

/** Reveals `[data-reveal]` and `.stagger` elements as they enter the viewport. */
export function useReveal(scope: RefObject<HTMLElement | null>, reduced: boolean) {
    useEffect(() => {
        const root = scope.current
        if (!root) return
        const items = Array.from(
            root.querySelectorAll<HTMLElement>("[data-reveal], .stagger, .split-text, .underline-sketch")
        )
        if (!items.length) return
        if (reduced || typeof IntersectionObserver === "undefined") {
            items.forEach((el) => el.classList.add("is-visible"))
            return
        }
        const io = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible")
                        io.unobserve(entry.target)
                    }
                })
            },
            { rootMargin: "0px 0px -10% 0px", threshold: 0.12 }
        )
        items.forEach((el) => io.observe(el))
        return () => io.disconnect()
    }, [scope, reduced])
}

/** Counts `[data-count]` elements up once they are on screen. */
export function useCountUp(scope: RefObject<HTMLElement | null>, reduced: boolean) {
    useEffect(() => {
        const root = scope.current
        if (!root) return
        const els = Array.from(root.querySelectorAll<HTMLElement>("[data-count]"))
        if (!els.length) return

        const format = (n: number, dec: number) =>
            n.toLocaleString(undefined, { minimumFractionDigits: dec, maximumFractionDigits: dec })

        const run = (el: HTMLElement) => {
            const target = parseFloat(el.dataset.count || "0")
            const dec = parseInt(el.dataset.decimals || "0", 10)
            if (reduced) {
                el.textContent = format(target, dec)
                return
            }
            const t0 = performance.now()
            const tick = (now: number) => {
                const p = Math.min(1, (now - t0) / 1600)
                el.textContent = format(target * (1 - Math.pow(1 - p, 4)), dec)
                if (p < 1) requestAnimationFrame(tick)
            }
            requestAnimationFrame(tick)
        }

        if (typeof IntersectionObserver === "undefined") {
            els.forEach(run)
            return
        }
        const io = new IntersectionObserver(
            (entries) =>
                entries.forEach((e) => {
                    if (e.isIntersecting) {
                        run(e.target as HTMLElement)
                        io.unobserve(e.target)
                    }
                }),
            { threshold: 0.5 }
        )
        els.forEach((el) => io.observe(el))
        return () => io.disconnect()
    }, [scope, reduced])
}

/** Everything a section component needs: styles, reveals and counters. */
export function useSection(theme: Theme, brandFont: boolean) {
    const ref = useRef<HTMLDivElement>(null)
    const reduced = useReducedMotion()
    const wrapper = useRootstock(theme, brandFont)
    useReveal(ref, reduced)
    useCountUp(ref, reduced)
    return { ref, wrapper, reduced }
}

export type CaptureState = "idle" | "busy" | "done" | "error"

/**
 * Email capture shared by the hero and footer sign-up forms.
 * With no endpoint set the form validates and confirms locally, which is what
 * you want while designing; set one to start collecting real submissions.
 */
export function useEmailCapture(endpoint: string, source: string) {
    const [email, setEmail] = useState("")
    const [state, setState] = useState<CaptureState>("idle")
    const [message, setMessage] = useState("")

    const submit = async (e: FormEvent) => {
        e.preventDefault()
        if (!/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(email.trim())) {
            setState("error")
            setMessage("Enter a valid email address, e.g. name@example.com")
            return
        }
        setState("busy")
        try {
            if (endpoint) {
                await fetch(endpoint, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email.trim(), source, submittedAt: new Date().toISOString() }),
                })
            }
            setEmail("")
            setState("done")
            setMessage("You're on the list — look out for our next planting update.")
        } catch {
            setState("error")
            setMessage("We couldn't reach the server. Please try again.")
        }
    }

    return { email, setEmail, state, message, submit }
}
