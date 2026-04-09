<script setup>
defineProps({ size: { type: Number, default: 36 } })
</script>

<template>
  <!-- 心镜 Logo: 像素心脏 + 心电波形 -->
  <svg :width="size" :height="size" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <!-- 玫红 → 珊瑚橙 渐变，复现图片暖色调 -->
      <linearGradient id="hg" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
        <stop offset="0%"   stop-color="#FF9AAD"/>
        <stop offset="50%"  stop-color="#FF6B8A"/>
        <stop offset="100%" stop-color="#F5873A"/>
      </linearGradient>
      <!-- 内部发光渐变 -->
      <radialGradient id="innerGlow" cx="40%" cy="35%" r="55%">
        <stop offset="0%"   stop-color="#FFCCD8" stop-opacity="0.6"/>
        <stop offset="100%" stop-color="#FF6B8A" stop-opacity="0"/>
      </radialGradient>
      <!-- 心形裁切区 -->
      <clipPath id="hc">
        <path d="M32 55 C24 49 7 38 7 23 C7 14.5 13.5 8 22 8 C26.8 8 30.5 10.5 32 13 C33.5 10.5 37.2 8 42 8 C50.5 8 57 14.5 57 23 C57 38 40 49 32 55Z"/>
      </clipPath>
    </defs>

    <!-- ① 心形主体 -->
    <path d="M32 55 C24 49 7 38 7 23 C7 14.5 13.5 8 22 8 C26.8 8 30.5 10.5 32 13 C33.5 10.5 37.2 8 42 8 C50.5 8 57 14.5 57 23 C57 38 40 49 32 55Z"
      fill="url(#hg)"/>

    <!-- ② 内部高光 -->
    <path d="M32 55 C24 49 7 38 7 23 C7 14.5 13.5 8 22 8 C26.8 8 30.5 10.5 32 13 C33.5 10.5 37.2 8 42 8 C50.5 8 57 14.5 57 23 C57 38 40 49 32 55Z"
      fill="url(#innerGlow)"/>

    <!-- ③ 像素网格（裁切在心形内） -->
    <g clip-path="url(#hc)" opacity="0.18">
      <line x1="15" y1="0"  x2="15" y2="64" stroke="white" stroke-width="0.6"/>
      <line x1="23" y1="0"  x2="23" y2="64" stroke="white" stroke-width="0.6"/>
      <line x1="31" y1="0"  x2="31" y2="64" stroke="white" stroke-width="0.6"/>
      <line x1="39" y1="0"  x2="39" y2="64" stroke="white" stroke-width="0.6"/>
      <line x1="47" y1="0"  x2="47" y2="64" stroke="white" stroke-width="0.6"/>
      <line x1="0"  y1="16" x2="64" y2="16" stroke="white" stroke-width="0.6"/>
      <line x1="0"  y1="24" x2="64" y2="24" stroke="white" stroke-width="0.6"/>
      <line x1="0"  y1="32" x2="64" y2="32" stroke="white" stroke-width="0.6"/>
      <line x1="0"  y1="40" x2="64" y2="40" stroke="white" stroke-width="0.6"/>
      <line x1="0"  y1="48" x2="64" y2="48" stroke="white" stroke-width="0.6"/>
    </g>

    <!-- ④ 心电波形线（裁切在心形内） -->
    <g clip-path="url(#hc)">
      <polyline
        points="7,32 13,32 15,26 17,38 20,26 22,38 24,22 26,42 28,32 36,32 38,26 40,38 43,26 45,38 47,22 49,42 51,32 57,32"
        fill="none"
        stroke="white"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
        opacity="0.88"
      />
    </g>

    <!-- ⑤ 像素风轮廓（心形描边，分段点状） -->
    <path d="M32 55 C24 49 7 38 7 23 C7 14.5 13.5 8 22 8 C26.8 8 30.5 10.5 32 13 C33.5 10.5 37.2 8 42 8 C50.5 8 57 14.5 57 23 C57 38 40 49 32 55Z"
      fill="none"
      stroke="white"
      stroke-width="1.2"
      stroke-opacity="0.35"
      stroke-dasharray="2 2"/>
  </svg>
</template>
