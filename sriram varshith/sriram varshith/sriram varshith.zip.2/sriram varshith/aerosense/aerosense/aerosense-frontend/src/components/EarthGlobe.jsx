
function EarthGlobe({ station, aqi }) {
  const mountRef = React.useRef(null);

  React.useEffect(() => {
    const mount = mountRef.current;
    const THREE = window.THREE;

    if (!THREE || !mount) {
      console.error("Three.js not loaded");
      return;
    }

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x02040a);

    const camera = new THREE.PerspectiveCamera(
      42,
      mount.clientWidth / mount.clientHeight,
      0.1,
      100
    );
    camera.position.z = 3.1;

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false
    });

    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    if ("outputColorSpace" in renderer) {
      renderer.outputColorSpace = THREE.SRGBColorSpace;
    }

    mount.appendChild(renderer.domElement);

    const loader = new THREE.TextureLoader();

    // EARTH
    const earthTexture = loader.load(
      "https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg"
    );

    if ("colorSpace" in earthTexture) {
      earthTexture.colorSpace = THREE.SRGBColorSpace;
    }

    const earthGeometry = new THREE.SphereGeometry(1, 128, 128);

    const earthMaterial = new THREE.MeshPhongMaterial({
      map: earthTexture,
      color: 0x53647c,
      shininess: 5
    });

    const earth = new THREE.Mesh(earthGeometry, earthMaterial);
    earth.rotation.y = Math.PI;

    // ONE GROUP FOR EARTH AND ALL MAP OBJECTS
    const earthGroup = new THREE.Group();
    earthGroup.add(earth);
    scene.add(earthGroup);

    // GOLDEN CITY LIGHTS
    const lightsTexture = loader.load(
      "https://threejs.org/examples/textures/planets/earth_lights_2048.png"
    );

    if ("colorSpace" in lightsTexture) {
      lightsTexture.colorSpace = THREE.SRGBColorSpace;
    }

    const lightsGeometry = new THREE.SphereGeometry(1.004, 128, 128);

    const lightsMaterial = new THREE.MeshBasicMaterial({
      map: lightsTexture,
      color: 0xffc66b,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });

    const cityLights = new THREE.Mesh(
      lightsGeometry,
      lightsMaterial
    );

    cityLights.rotation.y = Math.PI;
    earthGroup.add(cityLights);

    // AQI MARKERS
    const markerGroup = new THREE.Group();
    markerGroup.rotation.y = Math.PI;
    earthGroup.add(markerGroup);

    const cities = station && Number.isFinite(aqi)
      ? [{ name: station.name, lat: station.lat, lon: station.lon, aqi }]
      : [];

    function getAQIColor(aqi) {
      if (aqi <= 50)  return "#22c55e"; // Good
      if (aqi <= 100) return "#84cc16"; // Satisfactory
      if (aqi <= 200) return "#eab308"; // Moderate
      if (aqi <= 300) return "#f97316"; // Poor
      if (aqi <= 400) return "#ef4444"; // Very Poor
      return "#dc2626";                 // Severe
    }

    function createLabel(city, color) {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = 512;
      canvas.height = 120;

      ctx.fillStyle = "rgba(5, 12, 25, 0.88)";
      ctx.beginPath();
      ctx.roundRect(5, 5, 502, 110, 20);
      ctx.fill();

      ctx.strokeStyle = color;
      ctx.lineWidth = 5;
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 32px Arial";
      ctx.fillText(city.name, 25, 52);

      ctx.fillStyle = color;
      ctx.font = "bold 30px Arial";
      ctx.fillText("AQI " + city.aqi, 25, 91);

      const texture = new THREE.CanvasTexture(canvas);

      const material = new THREE.SpriteMaterial({
        map: texture,
        transparent: true,
        depthTest: true
      });

      const sprite = new THREE.Sprite(material);
      sprite.scale.set(0.55, 0.129, 1);

      return sprite;
    }

    cities.forEach((city) => {
      const lat = city.lat * Math.PI / 180;
      const lon = city.lon * Math.PI / 180;
      const radius = 1.025;

      const x = -radius * Math.cos(lat) * Math.cos(lon);
      const y = radius * Math.sin(lat);
      const z = radius * Math.cos(lat) * Math.sin(lon);

      const color = getAQIColor(city.aqi);

      const dotGeometry = new THREE.SphereGeometry(
        0.018, 16, 16
      );

      const dotMaterial = new THREE.MeshBasicMaterial({
        color: color
      });

      const dot = new THREE.Mesh(dotGeometry, dotMaterial);
      dot.position.set(x, y, z);
      markerGroup.add(dot);

      const glowGeometry = new THREE.SphereGeometry(
        0.035, 16, 16
      );

      const glowMaterial = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.25
      });

      const glow = new THREE.Mesh(glowGeometry, glowMaterial);
      glow.position.set(x, y, z);
      markerGroup.add(glow);

      const label = createLabel(city, color);
      label.position.set(x * 1.18, y * 1.18, z * 1.18);
      markerGroup.add(label);
    });

    // CLOUDS
    const cloudTexture = loader.load(
      "https://threejs.org/examples/textures/planets/earth_clouds_1024.png"
    );

    const cloudGeometry = new THREE.SphereGeometry(
      1.008, 128, 128
    );

    const cloudMaterial = new THREE.MeshPhongMaterial({
      map: cloudTexture,
      transparent: true,
      opacity: 0.12,
      depthWrite: false
    });

    const clouds = new THREE.Mesh(
      cloudGeometry,
      cloudMaterial
    );

    clouds.rotation.y = Math.PI;
    earthGroup.add(clouds);

    // ATMOSPHERE
    const atmosphereGeometry = new THREE.SphereGeometry(
      1.035, 128, 128
    );

    const atmosphereMaterial = new THREE.ShaderMaterial({
      vertexShader: `
        varying vec3 vNormal;
        varying vec3 vViewDirection;

        void main() {
          vec4 mvPosition =
            modelViewMatrix * vec4(position, 1.0);

          vNormal = normalize(normalMatrix * normal);
          vViewDirection = normalize(-mvPosition.xyz);

          gl_Position = projectionMatrix * mvPosition;
        }
      `,

      fragmentShader: `
        varying vec3 vNormal;
        varying vec3 vViewDirection;

        void main() {
          float fresnel = 1.0 - max(
            dot(
              normalize(vNormal),
              normalize(vViewDirection)
            ),
            0.0
          );

          float glow = pow(fresnel, 3.0);

          gl_FragColor = vec4(
            vec3(0.08, 0.35, 0.85),
            glow * 0.45
          );
        }
      `,

      transparent: true,
      blending: THREE.AdditiveBlending,
      side: THREE.FrontSide,
      depthWrite: false
    });

    const atmosphere = new THREE.Mesh(
      atmosphereGeometry,
      atmosphereMaterial
    );

    earthGroup.add(atmosphere);

    // LIGHTING
    const sunlight = new THREE.DirectionalLight(0xffffff, 0.7);
    sunlight.position.set(5, 2, 5);
    scene.add(sunlight);

    scene.add(
      new THREE.AmbientLight(0x25344d, 0.22)
    );

    // STARS
    const starGeometry = new THREE.BufferGeometry();
    const starPositions = [];

    for (let i = 0; i < 1800; i++) {
      starPositions.push(
        (Math.random() - 0.5) * 40,
        (Math.random() - 0.5) * 40,
        (Math.random() - 0.5) * 40
      );
    }

    starGeometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(starPositions, 3)
    );

    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.018,
      transparent: true,
      opacity: 0.75
    });

    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);

    // ZOOM
    let zoom = 3.1;

    function handleWheel(event) {
      event.preventDefault();

      zoom += event.deltaY * 0.002;
      zoom = Math.max(1.7, Math.min(6, zoom));

      camera.position.z = zoom;
    }

    renderer.domElement.addEventListener(
      "wheel",
      handleWheel,
      { passive: false }
    );

    // MANUAL MOUSE ROTATION
    let isDragging = false;
    let previousX = 0;
    let previousY = 0;

    function handlePointerDown(event) {
      isDragging = true;
      previousX = event.clientX;
      previousY = event.clientY;

      renderer.domElement.style.cursor = "grabbing";
      renderer.domElement.setPointerCapture(event.pointerId);
    }

    function handlePointerMove(event) {
      if (!isDragging) return;

      const deltaX = event.clientX - previousX;
      const deltaY = event.clientY - previousY;

      earthGroup.rotation.y += deltaX * 0.005;
      earthGroup.rotation.x += deltaY * 0.005;

      previousX = event.clientX;
      previousY = event.clientY;
    }

    function handlePointerUp() {
      isDragging = false;
      renderer.domElement.style.cursor = "grab";
    }

    renderer.domElement.addEventListener(
      "pointerdown", handlePointerDown
    );

    renderer.domElement.addEventListener(
      "pointermove", handlePointerMove
    );

    renderer.domElement.addEventListener(
      "pointerup", handlePointerUp
    );

    renderer.domElement.addEventListener(
      "pointercancel", handlePointerUp
    );

    // ANIMATION
    let animationId;

    function animate() {
      animationId = requestAnimationFrame(animate);

      if (!isDragging) {
        earthGroup.rotation.y += 0.0005;
      }

      stars.rotation.y += 0.00005;

      renderer.render(scene, camera);
    }

    animate();

    // RESIZE
    function handleResize() {
      const w = mount.clientWidth;
      const h = mount.clientHeight;

      if (!w || !h) return;

      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    }

    window.addEventListener("resize", handleResize);

    // CLEANUP
    return () => {
      cancelAnimationFrame(animationId);

      window.removeEventListener("resize", handleResize);

      renderer.domElement.removeEventListener(
        "wheel", handleWheel
      );

      renderer.domElement.removeEventListener(
        "pointerdown", handlePointerDown
      );

      renderer.domElement.removeEventListener(
        "pointermove", handlePointerMove
      );

      renderer.domElement.removeEventListener(
        "pointerup", handlePointerUp
      );

      renderer.domElement.removeEventListener(
        "pointercancel", handlePointerUp
      );

      earthGeometry.dispose();
      earthMaterial.dispose();
      earthTexture.dispose();

      lightsGeometry.dispose();
      lightsMaterial.dispose();
      lightsTexture.dispose();

      cloudGeometry.dispose();
      cloudMaterial.dispose();
      cloudTexture.dispose();

      atmosphereGeometry.dispose();
      atmosphereMaterial.dispose();

      starGeometry.dispose();
      starMaterial.dispose();

      markerGroup.children.forEach((child) => {
        if (child.geometry) child.geometry.dispose();

        if (child.material) {
          if (child.material.map) child.material.map.dispose();
          child.material.dispose();
        }
      });

      renderer.dispose();

      if (renderer.domElement.parentNode === mount) {
        mount.removeChild(renderer.domElement);
      }
    };
  }, [station, aqi]);

  return (
    <div
      ref={mountRef}
      style={{
        width: "100%",
        height: "500px",
        background: "#02040a",
        borderRadius: "20px",
        overflow: "hidden",
        cursor: "grab",
        touchAction: "none"
      }}
    />
  );
}

window.EarthGlobe = EarthGlobe;
