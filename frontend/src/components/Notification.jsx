import { useState, useEffect } from 'react';

/**
 * Notification Component (Pill Style)
 * Replaces Toast.jsx to avoid cache conflicts.
 */
export default function Notification({ message, type = 'info', onClose }) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Trigger enter animation
        const enterTimer = setTimeout(() => setIsVisible(true), 10);

        // Auto-close
        const closeTimer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(onClose, 300);
        }, 3500);

        return () => {
            clearTimeout(enterTimer);
            clearTimeout(closeTimer);
        };
    }, [onClose]);

    // Styles
    // Diseño ultra-minimalista: Solo texto blanco en la parte inferior
    const styleObj = {
        position: 'fixed',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        opacity: isVisible ? 1 : 0,
        zIndex: 9999,
        transition: 'opacity 0.3s ease-in-out',
        color: '#ffffff',
        fontSize: '14px',
        fontWeight: '500',
        textShadow: '0px 1px 4px rgba(0, 0, 0, 0.9)', // Sombra fuerte para legibilidad sobre el mapa
        pointerEvents: 'none', // Permitir clics a través del texto
        whiteSpace: 'nowrap',
        textAlign: 'center',
        fontFamily: 'system-ui, -apple-system, sans-serif'
    };

    // No usamos fondos ni bordes, solo el texto puro
    // Agregamos un pequeño icono inline sutil si es necesario, o solo texto
    const iconSpan = {
        marginRight: '8px',
        verticalAlign: 'middle',
        fontSize: '16px'
    };

    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ'
    };

    return (
        <div style={styleObj}>
            <span style={iconSpan}>{icons[type]}</span>
            {message}
        </div>
    );
}
