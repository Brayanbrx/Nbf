# Auth con refresh en cookie `HttpOnly` y access en `Bearer`

Este documento explica cómo está implementada en esta aplicación la autenticación basada en:

- `access token` JWT enviado en `Authorization: Bearer ...`
- `refresh token` JWT guardado en una cookie `HttpOnly`
- rotación e invalidación de refresh tokens en base de datos
- backend Spring Boot + frontend React/Axios

## 1. Idea general del patrón

La aplicación usa dos tokens distintos:

### `access token`

- vive poco tiempo
- el backend lo devuelve en el body del `login` y del `refresh`
- el frontend lo guarda en memoria
- el frontend lo manda en el header `Authorization: Bearer <token>`
- el filtro JWT del backend lo valida en cada request protegida

### `refresh token`

- vive más tiempo
- el backend lo genera en `login` y en cada `refresh`
- se guarda en cookie `HttpOnly`, no en JavaScript
- el navegador lo manda automáticamente al backend en `/auth/refresh` y `/auth/logout`
- además del JWT, se valida contra la tabla `auth_refresh_tokens`

La razón de hacerlo así es:

- el `access token` sirve para autenticar requests normales
- el `refresh token` no queda expuesto al código del frontend
- si el `access token` expira, el frontend intenta renovarlo con `/auth/refresh`
- si el `refresh token` fue revocado, expiró o no existe, la sesión se cae

## 2. Flujo real de esta aplicación

### Login

1. El frontend hace `POST /api/auth/login` con email y password.
2. El backend valida credenciales.
3. El backend revoca refresh tokens anteriores del usuario.
4. El backend crea:
   - un `access token`
   - un `refresh token` con `jti` (`tokenId`)
5. El backend guarda el `tokenId` del refresh en base de datos.
6. El backend devuelve:
   - el `access token` en el body
   - el `refresh token` en `Set-Cookie` como cookie `HttpOnly`

### Uso normal

1. El frontend guarda el `access token` en memoria.
2. Cada request protegida agrega `Authorization: Bearer <accessToken>`.
3. `JwtAuthenticationFilter` valida el JWT y crea el `SecurityContext`.

### Refresh

1. Si una request protegida responde `401`, el frontend intenta `POST /api/auth/refresh`.
2. El navegador manda automáticamente la cookie `refresh_token`.
3. El backend:
   - extrae la cookie
   - parsea el refresh JWT
   - busca el `tokenId` en DB
   - valida que pertenezca al usuario, no esté revocado y no haya expirado
   - revoca el refresh anterior
   - crea uno nuevo
4. El backend devuelve un nuevo `access token` en body y un nuevo `refresh token` en cookie.
5. El frontend reintenta la request original con el nuevo bearer.

### Logout

1. El frontend hace `POST /api/auth/logout`.
2. El navegador manda la cookie `refresh_token`.
3. El backend revoca ese refresh token en DB.
4. El backend limpia la cookie.
5. El frontend limpia el `access token` en memoria.

## 3. Contrato HTTP real del backend

La app backend corre bajo `server.servlet.context-path=/api`, por eso los endpoints reales son:

- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`
- `GET /api/auth/me`

### Login

Request:

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@dashboardtya.local",
  "password": "Admin12345"
}
```

Response:

```http
HTTP/1.1 200 OK
Set-Cookie: refresh_token=...; Path=/api/auth; HttpOnly; SameSite=Lax
Content-Type: application/json

{
  "success": true,
  "message": "Inicio de sesión exitoso.",
  "data": {
    "access_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

### Refresh

Request:

```http
POST /api/auth/refresh
Cookie: refresh_token=...
```

Response:

```http
HTTP/1.1 200 OK
Set-Cookie: refresh_token=...nuevo...; Path=/api/auth; HttpOnly; SameSite=Lax
Content-Type: application/json

{
  "success": true,
  "message": "Sesión renovada correctamente.",
  "data": {
    "access_token": "eyJ...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

### Request protegida

```http
GET /api/auth/me
Authorization: Bearer eyJ...
```

## 4. Piezas clave en esta aplicación

### Backend

- `AuthController`: expone `login`, `refresh`, `logout`, `me`
- `LoginUseCase`: autentica y genera sesión inicial
- `RefreshSessionUseCase`: valida refresh y rota tokens
- `LogoutUseCase`: revoca refresh y hace logout idempotente
- `JjwtTokenService`: crea y parsea access/refresh JWT
- `HttpRefreshCookieService`: escribe, limpia y extrae la cookie `HttpOnly`
- `JwtAuthenticationFilter`: valida el bearer en requests protegidas
- `SecurityConfig`: deja `login/refresh/logout` públicos y el resto autenticado
- `AuthRefreshTokenRepository*`: persiste y revoca refresh tokens

### Frontend

- `rawClient`: axios para llamadas de auth que dependen de cookie
- `createHttpClient`: interceptor que agrega bearer y hace refresh automático
- `httpClient`: cliente principal para endpoints protegidos
- `sessionStore`: guarda el `accessToken` en memoria y hace bootstrap
- `useLoginMutation`: guarda access token e hidrata usuario
- `refreshAccessTokenFn`: llama `/auth/refresh`
- `logoutSession`: llama `/auth/logout`

## 5. Detalles importantes de seguridad

### El refresh no se guarda en JavaScript

Eso se logra porque el backend lo manda como cookie `HttpOnly`:

- el navegador la guarda
- el navegador la manda sola a `/api/auth`
- el frontend no puede leerla con `document.cookie`

### El access sí lo usa el frontend

El frontend necesita leerlo para poder mandar:

```http
Authorization: Bearer <access-token>
```

En esta app el `accessToken` se guarda en `sessionStore` en memoria.

### Hay rotación de refresh token

Cada vez que se usa `/auth/refresh`:

- el token anterior se revoca
- se crea un refresh nuevo
- se emite una cookie nueva

Eso reduce replay si un refresh viejo se filtra.

### El refresh se valida en dos capas

No basta con validar la firma del JWT. También se revisa en DB:

- que el `tokenId` exista
- que pertenezca al usuario correcto
- que no esté revocado
- que no esté expirado

## 6. Configuración necesaria

### JWT

- `auth.jwt.secret`
- `auth.jwt.issuer`
- `auth.jwt.access-ttl-seconds`
- `auth.jwt.refresh-ttl-seconds`

### Cookie

- `auth.cookie.name`
- `auth.cookie.same-site`
- `auth.cookie.domain`
- `auth.cookie.path`
- `auth.cookie.secure`

### CORS

Como aquí se usan cookies, el backend debe permitir credenciales:

- `cors.allow-credentials: true`
- el frontend usa `withCredentials: true`
- `allowed-origins` no debe ser `*` cuando se usan credenciales

## 7. Nota importante sobre el frontend actual

El backend responde con un wrapper:

```json
{
  "success": true,
  "message": "...",
  "data": {
    "access_token": "...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

Pero en el frontend actual hay llamadas que leen la respuesta como si no existiera el wrapper:

- `loginWithEmail.ts` retorna `res.data`
- `refreshSession.ts` intenta leer `res.data.access`
- `getMe.ts` retorna `res.data`

Entonces, para que frontend y backend queden 100% alineados, esas funciones deberían leer `res.data.data` y mapear `access_token` a `accessToken`. Este documento refleja el contrato real del backend y el flujo arquitectónico real que implementa la app.

## 8. Código completo necesario en esta aplicación

## Backend

### `backend/src/main/java/com/dashboardtya/modules/auth/api/AuthController.java`

```java
package com.dashboardtya.modules.auth.api;

import com.dashboardtya.common.security.AuthenticatedUserPrincipal;
import com.dashboardtya.common.security.CurrentAuthenticatedUserProvider;
import com.dashboardtya.common.web.ApiResponse;
import com.dashboardtya.modules.audit.domain.model.AuditAction;
import com.dashboardtya.modules.audit.domain.model.AuditEntityType;
import com.dashboardtya.modules.audit.infrastructure.service.AuditTrailService;
import com.dashboardtya.modules.auth.api.request.LoginRequest;
import com.dashboardtya.modules.auth.api.response.AccessTokenResponse;
import com.dashboardtya.modules.auth.api.response.MeResponse;
import com.dashboardtya.modules.auth.application.GetCurrentUserUseCase;
import com.dashboardtya.modules.auth.application.LoginUseCase;
import com.dashboardtya.modules.auth.application.LogoutUseCase;
import com.dashboardtya.modules.auth.application.RefreshSessionUseCase;
import com.dashboardtya.modules.auth.application.dto.CurrentUserResult;
import com.dashboardtya.modules.auth.application.dto.LoginCommand;
import com.dashboardtya.modules.auth.domain.model.AuthSessionResult;
import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.service.AuthUserRepository;
import com.dashboardtya.modules.auth.domain.service.RefreshCookieService;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Optional;

@RestController
@RequestMapping("/auth")
@Tag(name = "Auth", description = "Autenticación y sesión")
public class AuthController {

    private final LoginUseCase loginUseCase;
    private final RefreshSessionUseCase refreshSessionUseCase;
    private final LogoutUseCase logoutUseCase;
    private final GetCurrentUserUseCase getCurrentUserUseCase;
    private final RefreshCookieService refreshCookieService;
    private final CurrentAuthenticatedUserProvider currentAuthenticatedUserProvider;
    private final AuthUserRepository authUserRepository;
    private final AuditTrailService auditTrailService;

    public AuthController(
            LoginUseCase loginUseCase,
            RefreshSessionUseCase refreshSessionUseCase,
            LogoutUseCase logoutUseCase,
            GetCurrentUserUseCase getCurrentUserUseCase,
            RefreshCookieService refreshCookieService,
            CurrentAuthenticatedUserProvider currentAuthenticatedUserProvider,
            AuthUserRepository authUserRepository,
            AuditTrailService auditTrailService
    ) {
        this.loginUseCase = loginUseCase;
        this.refreshSessionUseCase = refreshSessionUseCase;
        this.logoutUseCase = logoutUseCase;
        this.getCurrentUserUseCase = getCurrentUserUseCase;
        this.refreshCookieService = refreshCookieService;
        this.currentAuthenticatedUserProvider = currentAuthenticatedUserProvider;
        this.authUserRepository = authUserRepository;
        this.auditTrailService = auditTrailService;
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<AccessTokenResponse>> login(
            @Valid @RequestBody LoginRequest request,
            HttpServletResponse response
    ) {
        AuthSessionResult sessionResult = loginUseCase.execute(
                new LoginCommand(request.email(), request.password())
        );

        refreshCookieService.writeRefreshTokenCookie(response, sessionResult.refreshToken());

        AccessTokenResponse payload = new AccessTokenResponse(
                sessionResult.accessToken(),
                sessionResult.tokenType(),
                sessionResult.expiresIn()
        );

        Optional<AuthUser> authenticatedUser = authUserRepository.findByEmail(
                request.email().trim().toLowerCase(Locale.ROOT)
        );

        LinkedHashMap<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("email", request.email().trim().toLowerCase(Locale.ROOT));
        metadata.put("token_type", sessionResult.tokenType());
        metadata.put("expires_in", sessionResult.expiresIn());

        if (authenticatedUser.isPresent()) {
            AuthUser user = authenticatedUser.get();
            auditTrailService.recordExplicitActor(
                    user.id(),
                    user.email(),
                    user.fullName(),
                    AuditAction.LOGIN,
                    AuditEntityType.AUTH,
                    user.id(),
                    "Inicio de sesión exitoso.",
                    metadata
            );
        } else {
            auditTrailService.recordExplicitActor(
                    null,
                    request.email().trim().toLowerCase(Locale.ROOT),
                    null,
                    AuditAction.LOGIN,
                    AuditEntityType.AUTH,
                    null,
                    "Inicio de sesión exitoso.",
                    metadata
            );
        }

        return ResponseEntity.ok(ApiResponse.success("Inicio de sesión exitoso.", payload));
    }

    @PostMapping("/refresh")
    public ResponseEntity<ApiResponse<AccessTokenResponse>> refresh(
            HttpServletRequest request,
            HttpServletResponse response
    ) {
        String rawRefreshToken = refreshCookieService.extractRefreshToken(request);
        AuthSessionResult sessionResult = refreshSessionUseCase.execute(rawRefreshToken);

        refreshCookieService.writeRefreshTokenCookie(response, sessionResult.refreshToken());

        AccessTokenResponse payload = new AccessTokenResponse(
                sessionResult.accessToken(),
                sessionResult.tokenType(),
                sessionResult.expiresIn()
        );

        LinkedHashMap<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("token_type", sessionResult.tokenType());
        metadata.put("expires_in", sessionResult.expiresIn());

        auditTrailService.record(
                AuditAction.TOKEN_REFRESH,
                AuditEntityType.AUTH,
                null,
                "Renovación de sesión mediante refresh token.",
                metadata
        );

        return ResponseEntity.ok(ApiResponse.success("Sesión renovada correctamente.", payload));
    }

    @PostMapping("/logout")
    public ResponseEntity<ApiResponse<Void>> logout(
            HttpServletRequest request,
            HttpServletResponse response
    ) {
        String rawRefreshToken = refreshCookieService.extractRefreshToken(request);
        logoutUseCase.execute(rawRefreshToken);
        refreshCookieService.clearRefreshTokenCookie(response);

        auditTrailService.record(
                AuditAction.LOGOUT,
                AuditEntityType.AUTH,
                null,
                "Cierre de sesión ejecutado.",
                null
        );

        return ResponseEntity.ok(ApiResponse.success("Sesión cerrada correctamente.", null));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<MeResponse>> me() {
        AuthenticatedUserPrincipal currentUser = currentAuthenticatedUserProvider.requireCurrentUser();
        CurrentUserResult currentUserResult = getCurrentUserUseCase.execute(currentUser.userId());

        MeResponse payload = new MeResponse(
                currentUserResult.id(),
                currentUserResult.email(),
                currentUserResult.fullName(),
                currentUserResult.roles(),
                currentUserResult.permissions()
        );

        return ResponseEntity.ok(ApiResponse.success("Usuario autenticado obtenido correctamente.", payload));
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/application/LoginUseCase.java`

```java
package com.dashboardtya.modules.auth.application;

import com.dashboardtya.modules.auth.application.dto.LoginCommand;
import com.dashboardtya.modules.auth.domain.exception.InactiveUserException;
import com.dashboardtya.modules.auth.domain.exception.InvalidCredentialsException;
import com.dashboardtya.modules.auth.domain.model.AuthSessionResult;
import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.service.AuthRefreshTokenRepository;
import com.dashboardtya.modules.auth.domain.service.AuthUserRepository;
import com.dashboardtya.modules.auth.domain.service.JwtTokenService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Locale;
import java.util.UUID;

@Service
public class LoginUseCase {

    private final AuthUserRepository authUserRepository;
    private final AuthRefreshTokenRepository authRefreshTokenRepository;
    private final JwtTokenService jwtTokenService;
    private final PasswordEncoder passwordEncoder;

    public LoginUseCase(
            AuthUserRepository authUserRepository,
            AuthRefreshTokenRepository authRefreshTokenRepository,
            JwtTokenService jwtTokenService,
            PasswordEncoder passwordEncoder
    ) {
        this.authUserRepository = authUserRepository;
        this.authRefreshTokenRepository = authRefreshTokenRepository;
        this.jwtTokenService = jwtTokenService;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional
    public AuthSessionResult execute(LoginCommand command) {
        String normalizedEmail = normalizeEmail(command.email());

        AuthUser user = authUserRepository.findByEmail(normalizedEmail)
                .orElseThrow(InvalidCredentialsException::new);

        if (!user.active()) {
            throw new InactiveUserException();
        }

        boolean passwordMatches = passwordEncoder.matches(command.password(), user.passwordHash());
        if (!passwordMatches) {
            throw new InvalidCredentialsException();
        }

        Instant now = Instant.now();
        authRefreshTokenRepository.revokeAllByUserId(user.id(), now);

        UUID tokenId = UUID.randomUUID();
        Instant refreshExpiresAt = now.plusSeconds(jwtTokenService.getRefreshTokenTtlSeconds());

        authRefreshTokenRepository.save(user.id(), tokenId, refreshExpiresAt);

        String accessToken = jwtTokenService.createAccessToken(user);
        String refreshToken = jwtTokenService.createRefreshToken(user, tokenId);

        return new AuthSessionResult(
                accessToken,
                refreshToken,
                "Bearer",
                jwtTokenService.getAccessTokenTtlSeconds()
        );
    }

    private String normalizeEmail(String email) {
        if (email == null || email.isBlank()) {
            throw new InvalidCredentialsException();
        }
        return email.trim().toLowerCase(Locale.ROOT);
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/application/RefreshSessionUseCase.java`

```java
package com.dashboardtya.modules.auth.application;

import com.dashboardtya.modules.auth.domain.exception.InactiveUserException;
import com.dashboardtya.modules.auth.domain.exception.InvalidRefreshTokenException;
import com.dashboardtya.modules.auth.domain.model.AuthSessionResult;
import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.model.RefreshTokenClaims;
import com.dashboardtya.modules.auth.domain.model.StoredRefreshToken;
import com.dashboardtya.modules.auth.domain.service.AuthRefreshTokenRepository;
import com.dashboardtya.modules.auth.domain.service.AuthUserRepository;
import com.dashboardtya.modules.auth.domain.service.JwtTokenService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Service
public class RefreshSessionUseCase {

    private final AuthRefreshTokenRepository authRefreshTokenRepository;
    private final AuthUserRepository authUserRepository;
    private final JwtTokenService jwtTokenService;

    public RefreshSessionUseCase(
            AuthRefreshTokenRepository authRefreshTokenRepository,
            AuthUserRepository authUserRepository,
            JwtTokenService jwtTokenService
    ) {
        this.authRefreshTokenRepository = authRefreshTokenRepository;
        this.authUserRepository = authUserRepository;
        this.jwtTokenService = jwtTokenService;
    }

    @Transactional
    public AuthSessionResult execute(String rawRefreshToken) {
        if (rawRefreshToken == null || rawRefreshToken.isBlank()) {
            throw new InvalidRefreshTokenException();
        }

        RefreshTokenClaims claims = jwtTokenService.parseRefreshToken(rawRefreshToken);

        StoredRefreshToken storedRefreshToken = authRefreshTokenRepository.findByTokenId(claims.tokenId())
                .orElseThrow(InvalidRefreshTokenException::new);

        Instant now = Instant.now();

        boolean tokenBelongsToUser = storedRefreshToken.userId().equals(claims.userId());
        if (!tokenBelongsToUser || !storedRefreshToken.isUsableAt(now)) {
            throw new InvalidRefreshTokenException();
        }

        AuthUser user = authUserRepository.findActiveById(claims.userId())
                .orElseThrow(InvalidRefreshTokenException::new);

        if (!user.active()) {
            throw new InactiveUserException();
        }

        authRefreshTokenRepository.revoke(storedRefreshToken.tokenId(), now);

        UUID newTokenId = UUID.randomUUID();
        Instant refreshExpiresAt = now.plusSeconds(jwtTokenService.getRefreshTokenTtlSeconds());

        authRefreshTokenRepository.save(user.id(), newTokenId, refreshExpiresAt);

        String accessToken = jwtTokenService.createAccessToken(user);
        String refreshToken = jwtTokenService.createRefreshToken(user, newTokenId);

        return new AuthSessionResult(
                accessToken,
                refreshToken,
                "Bearer",
                jwtTokenService.getAccessTokenTtlSeconds()
        );
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/application/LogoutUseCase.java`

```java
package com.dashboardtya.modules.auth.application;

import com.dashboardtya.modules.auth.domain.model.RefreshTokenClaims;
import com.dashboardtya.modules.auth.domain.service.AuthRefreshTokenRepository;
import com.dashboardtya.modules.auth.domain.service.JwtTokenService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
public class LogoutUseCase {

    private final AuthRefreshTokenRepository authRefreshTokenRepository;
    private final JwtTokenService jwtTokenService;

    public LogoutUseCase(
            AuthRefreshTokenRepository authRefreshTokenRepository,
            JwtTokenService jwtTokenService
    ) {
        this.authRefreshTokenRepository = authRefreshTokenRepository;
        this.jwtTokenService = jwtTokenService;
    }

    @Transactional
    public void execute(String rawRefreshToken) {
        if (rawRefreshToken == null || rawRefreshToken.isBlank()) {
            return;
        }

        try {
            RefreshTokenClaims claims = jwtTokenService.parseRefreshToken(rawRefreshToken);
            authRefreshTokenRepository.revoke(claims.tokenId(), Instant.now());
        } catch (Exception ignored) {
            // Logout debe ser seguro e idempotente aunque el token ya no sea válido.
        }
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/jwt/JjwtTokenService.java`

```java
package com.dashboardtya.modules.auth.infrastructure.jwt;

import com.dashboardtya.common.config.properties.AuthJwtProperties;
import com.dashboardtya.modules.access.domain.model.RoleCode;
import com.dashboardtya.modules.auth.domain.exception.InvalidCredentialsException;
import com.dashboardtya.modules.auth.domain.exception.InvalidRefreshTokenException;
import com.dashboardtya.modules.auth.domain.model.AccessTokenClaims;
import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.model.RefreshTokenClaims;
import com.dashboardtya.modules.auth.domain.service.JwtTokenService;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;
import java.util.UUID;

@Component
public class JjwtTokenService implements JwtTokenService {

    private static final String CLAIM_TOKEN_TYPE = "token_type";
    private static final String TOKEN_TYPE_ACCESS = "access";
    private static final String TOKEN_TYPE_REFRESH = "refresh";
    private static final String CLAIM_ROLE = "role";
    private static final String CLAIM_EMAIL = "email";

    private final AuthJwtProperties authJwtProperties;
    private final SecretKey secretKey;

    public JjwtTokenService(AuthJwtProperties authJwtProperties) {
        this.authJwtProperties = authJwtProperties;
        this.secretKey = Keys.hmacShaKeyFor(authJwtProperties.getSecret().getBytes(StandardCharsets.UTF_8));
    }

    @Override
    public String createAccessToken(AuthUser user) {
        Instant now = Instant.now();
        Instant expiresAt = now.plusSeconds(authJwtProperties.getAccessTtlSeconds());

        return Jwts.builder()
                .subject(user.id().toString())
                .issuer(authJwtProperties.getIssuer())
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiresAt))
                .claim(CLAIM_TOKEN_TYPE, TOKEN_TYPE_ACCESS)
                .claim(CLAIM_EMAIL, user.email())
                .claim(CLAIM_ROLE, user.roleCode().name())
                .signWith(secretKey)
                .compact();
    }

    @Override
    public String createRefreshToken(AuthUser user, UUID tokenId) {
        Instant now = Instant.now();
        Instant expiresAt = now.plusSeconds(authJwtProperties.getRefreshTtlSeconds());

        return Jwts.builder()
                .id(tokenId.toString())
                .subject(user.id().toString())
                .issuer(authJwtProperties.getIssuer())
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiresAt))
                .claim(CLAIM_TOKEN_TYPE, TOKEN_TYPE_REFRESH)
                .signWith(secretKey)
                .compact();
    }

    @Override
    public AccessTokenClaims parseAccessToken(String token) {
        try {
            Claims claims = parseClaims(token);

            String tokenType = claims.get(CLAIM_TOKEN_TYPE, String.class);
            if (!TOKEN_TYPE_ACCESS.equals(tokenType)) {
                throw new InvalidCredentialsException();
            }

            UUID userId = UUID.fromString(claims.getSubject());
            String email = claims.get(CLAIM_EMAIL, String.class);
            RoleCode roleCode = RoleCode.valueOf(claims.get(CLAIM_ROLE, String.class));

            return new AccessTokenClaims(userId, email, roleCode);
        } catch (JwtException | IllegalArgumentException ex) {
            throw new InvalidCredentialsException();
        }
    }

    @Override
    public RefreshTokenClaims parseRefreshToken(String token) {
        try {
            Claims claims = parseClaims(token);

            String tokenType = claims.get(CLAIM_TOKEN_TYPE, String.class);
            if (!TOKEN_TYPE_REFRESH.equals(tokenType)) {
                throw new InvalidRefreshTokenException();
            }

            UUID userId = UUID.fromString(claims.getSubject());
            UUID tokenId = UUID.fromString(claims.getId());

            return new RefreshTokenClaims(userId, tokenId);
        } catch (JwtException | IllegalArgumentException ex) {
            throw new InvalidRefreshTokenException();
        }
    }

    @Override
    public long getAccessTokenTtlSeconds() {
        return authJwtProperties.getAccessTtlSeconds();
    }

    @Override
    public long getRefreshTokenTtlSeconds() {
        return authJwtProperties.getRefreshTtlSeconds();
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(secretKey)
                .requireIssuer(authJwtProperties.getIssuer())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/cookie/HttpRefreshCookieService.java`

```java
package com.dashboardtya.modules.auth.infrastructure.cookie;

import com.dashboardtya.common.config.properties.AuthCookieProperties;
import com.dashboardtya.modules.auth.domain.service.RefreshCookieService;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;

@Component
public class HttpRefreshCookieService implements RefreshCookieService {

    private final AuthCookieProperties authCookieProperties;

    public HttpRefreshCookieService(AuthCookieProperties authCookieProperties) {
        this.authCookieProperties = authCookieProperties;
    }

    @Override
    public void writeRefreshTokenCookie(HttpServletResponse response, String refreshToken) {
        ResponseCookie.ResponseCookieBuilder builder = ResponseCookie.from(authCookieProperties.getName(), refreshToken)
                .httpOnly(true)
                .secure(parseBoolean(authCookieProperties.getSecure()))
                .path(authCookieProperties.getPath())
                .sameSite(authCookieProperties.getSameSite());

        if (authCookieProperties.getDomain() != null && !authCookieProperties.getDomain().isBlank()) {
            builder.domain(authCookieProperties.getDomain());
        }

        response.addHeader(HttpHeaders.SET_COOKIE, builder.build().toString());
    }

    @Override
    public void clearRefreshTokenCookie(HttpServletResponse response) {
        ResponseCookie.ResponseCookieBuilder builder = ResponseCookie.from(authCookieProperties.getName(), "")
                .httpOnly(true)
                .secure(parseBoolean(authCookieProperties.getSecure()))
                .path(authCookieProperties.getPath())
                .sameSite(authCookieProperties.getSameSite())
                .maxAge(0);

        if (authCookieProperties.getDomain() != null && !authCookieProperties.getDomain().isBlank()) {
            builder.domain(authCookieProperties.getDomain());
        }

        response.addHeader(HttpHeaders.SET_COOKIE, builder.build().toString());
    }

    @Override
    public String extractRefreshToken(HttpServletRequest request) {
        Cookie[] cookies = request.getCookies();
        if (cookies == null) {
            return null;
        }

        for (Cookie cookie : cookies) {
            if (authCookieProperties.getName().equals(cookie.getName())) {
                return cookie.getValue();
            }
        }

        return null;
    }

    private boolean parseBoolean(String value) {
        if (value == null) {
            return false;
        }
        return "true".equalsIgnoreCase(value) || "1".equals(value);
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/security/JwtAuthenticationFilter.java`

```java
package com.dashboardtya.modules.auth.infrastructure.security;

import com.dashboardtya.common.security.AuthenticatedUserPrincipal;
import com.dashboardtya.modules.auth.domain.model.AccessTokenClaims;
import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.service.AuthUserRepository;
import com.dashboardtya.modules.auth.domain.service.JwtTokenService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final String BEARER_PREFIX = "Bearer ";

    private final JwtTokenService jwtTokenService;
    private final AuthUserRepository authUserRepository;

    public JwtAuthenticationFilter(
            JwtTokenService jwtTokenService,
            AuthUserRepository authUserRepository
    ) {
        this.jwtTokenService = jwtTokenService;
        this.authUserRepository = authUserRepository;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        String authorizationHeader = request.getHeader(HttpHeaders.AUTHORIZATION);

        if (!StringUtils.hasText(authorizationHeader) || !authorizationHeader.startsWith(BEARER_PREFIX)) {
            filterChain.doFilter(request, response);
            return;
        }

        String accessToken = authorizationHeader.substring(BEARER_PREFIX.length()).trim();

        try {
            AccessTokenClaims claims = jwtTokenService.parseAccessToken(accessToken);

            AuthUser user = authUserRepository.findActiveById(claims.userId()).orElse(null);
            if (user != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                AuthenticatedUserPrincipal principal = new AuthenticatedUserPrincipal(
                        user.id(),
                        user.email(),
                        user.fullName(),
                        user.roleCode()
                );

                UsernamePasswordAuthenticationToken authentication
                        = new UsernamePasswordAuthenticationToken(
                                principal,
                                null,
                                List.of(new SimpleGrantedAuthority("ROLE_" + user.roleCode().name()))
                        );

                authentication.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authentication);
            }
        } catch (RuntimeException ignored) {
            SecurityContextHolder.clearContext();
        }

        filterChain.doFilter(request, response);
    }
}
```

### `backend/src/main/java/com/dashboardtya/common/security/SecurityConfig.java`

```java
package com.dashboardtya.common.security;

import com.dashboardtya.modules.auth.infrastructure.security.JwtAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfigurationSource;

@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http,
            CorsConfigurationSource corsConfigurationSource,
            RestAuthenticationEntryPoint restAuthenticationEntryPoint,
            RestAccessDeniedHandler restAccessDeniedHandler,
            JwtAuthenticationFilter jwtAuthenticationFilter
    ) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .cors(cors -> cors.configurationSource(corsConfigurationSource))
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .exceptionHandling(exception -> exception
                .authenticationEntryPoint(restAuthenticationEntryPoint)
                .accessDeniedHandler(restAccessDeniedHandler))
                .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.GET, "/public/**").permitAll()
                .requestMatchers("/actuator/health", "/actuator/info").permitAll()
                .requestMatchers("/v3/api-docs/**", "/swagger-ui/**", "/swagger-ui.html").permitAll()
                .requestMatchers(HttpMethod.POST, "/auth/login", "/auth/refresh", "/auth/logout").permitAll()
                .requestMatchers("/error").permitAll()
                .anyRequest().authenticated())
                .httpBasic(AbstractHttpConfigurer::disable)
                .formLogin(AbstractHttpConfigurer::disable)
                .logout(AbstractHttpConfigurer::disable)
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/service/JwtTokenService.java`

```java
package com.dashboardtya.modules.auth.domain.service;

import com.dashboardtya.modules.auth.domain.model.AccessTokenClaims;
import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.model.RefreshTokenClaims;

import java.util.UUID;

public interface JwtTokenService {

    String createAccessToken(AuthUser user);

    String createRefreshToken(AuthUser user, UUID tokenId);

    AccessTokenClaims parseAccessToken(String token);

    RefreshTokenClaims parseRefreshToken(String token);

    long getAccessTokenTtlSeconds();

    long getRefreshTokenTtlSeconds();
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/service/RefreshCookieService.java`

```java
package com.dashboardtya.modules.auth.domain.service;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

public interface RefreshCookieService {

    void writeRefreshTokenCookie(HttpServletResponse response, String refreshToken);

    void clearRefreshTokenCookie(HttpServletResponse response);

    String extractRefreshToken(HttpServletRequest request);
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/service/AuthRefreshTokenRepository.java`

```java
package com.dashboardtya.modules.auth.domain.service;

import com.dashboardtya.modules.auth.domain.model.StoredRefreshToken;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

public interface AuthRefreshTokenRepository {

    StoredRefreshToken save(UUID userId, UUID tokenId, Instant expiresAt);

    Optional<StoredRefreshToken> findByTokenId(UUID tokenId);

    void revoke(UUID tokenId, Instant revokedAt);

    void revokeAllByUserId(UUID userId, Instant revokedAt);
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/service/AuthUserRepository.java`

```java
package com.dashboardtya.modules.auth.domain.service;

import com.dashboardtya.modules.auth.domain.model.AuthUser;

import java.util.Optional;
import java.util.UUID;

public interface AuthUserRepository {

    Optional<AuthUser> findByEmail(String email);

    Optional<AuthUser> findActiveById(UUID userId);

    boolean existsByEmail(String email);

    AuthUser save(AuthUser user);
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/model/AuthSessionResult.java`

```java
package com.dashboardtya.modules.auth.domain.model;

public record AuthSessionResult(
        String accessToken,
        String refreshToken,
        String tokenType,
        long expiresIn
        ) {

}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/model/AccessTokenClaims.java`

```java
package com.dashboardtya.modules.auth.domain.model;

import com.dashboardtya.modules.access.domain.model.RoleCode;

import java.util.UUID;

public record AccessTokenClaims(
        UUID userId,
        String email,
        RoleCode roleCode
        ) {

}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/model/RefreshTokenClaims.java`

```java
package com.dashboardtya.modules.auth.domain.model;

import java.util.UUID;

public record RefreshTokenClaims(
        UUID userId,
        UUID tokenId
        ) {

}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/model/StoredRefreshToken.java`

```java
package com.dashboardtya.modules.auth.domain.model;

import java.time.Instant;
import java.util.UUID;

public record StoredRefreshToken(
        UUID id,
        UUID tokenId,
        UUID userId,
        Instant expiresAt,
        Instant revokedAt
        ) {

    public boolean isUsableAt(Instant instant) {
        return revokedAt == null && expiresAt != null && expiresAt.isAfter(instant);
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/domain/model/AuthUser.java`

```java
package com.dashboardtya.modules.auth.domain.model;

import com.dashboardtya.modules.access.domain.model.RoleCode;

import java.util.UUID;

public record AuthUser(
        UUID id,
        String email,
        String fullName,
        String passwordHash,
        RoleCode roleCode,
        boolean active
        ) {

}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/persistence/AuthRefreshTokenRepositoryAdapter.java`

```java
package com.dashboardtya.modules.auth.infrastructure.persistence;

import com.dashboardtya.modules.auth.domain.model.StoredRefreshToken;
import com.dashboardtya.modules.auth.domain.service.AuthRefreshTokenRepository;
import com.dashboardtya.modules.auth.infrastructure.persistence.entity.AuthRefreshTokenEntity;
import com.dashboardtya.modules.auth.infrastructure.persistence.entity.AuthUserEntity;
import com.dashboardtya.modules.auth.infrastructure.persistence.repository.AuthRefreshTokenJpaRepository;
import jakarta.persistence.EntityManager;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

@Component
public class AuthRefreshTokenRepositoryAdapter implements AuthRefreshTokenRepository {

    private final AuthRefreshTokenJpaRepository authRefreshTokenJpaRepository;
    private final EntityManager entityManager;

    public AuthRefreshTokenRepositoryAdapter(
            AuthRefreshTokenJpaRepository authRefreshTokenJpaRepository,
            EntityManager entityManager
    ) {
        this.authRefreshTokenJpaRepository = authRefreshTokenJpaRepository;
        this.entityManager = entityManager;
    }

    @Override
    public StoredRefreshToken save(UUID userId, UUID tokenId, Instant expiresAt) {
        AuthRefreshTokenEntity entity = new AuthRefreshTokenEntity();
        AuthUserEntity userReference = entityManager.getReference(AuthUserEntity.class, userId);

        entity.setTokenId(tokenId);
        entity.setUser(userReference);
        entity.setExpiresAt(expiresAt);
        entity.setRevokedAt(null);

        AuthRefreshTokenEntity saved = authRefreshTokenJpaRepository.save(entity);
        return toDomain(saved);
    }

    @Override
    public Optional<StoredRefreshToken> findByTokenId(UUID tokenId) {
        return authRefreshTokenJpaRepository.findByTokenId(tokenId)
                .map(this::toDomain);
    }

    @Override
    public void revoke(UUID tokenId, Instant revokedAt) {
        authRefreshTokenJpaRepository.revokeByTokenId(tokenId, revokedAt);
    }

    @Override
    public void revokeAllByUserId(UUID userId, Instant revokedAt) {
        authRefreshTokenJpaRepository.revokeAllActiveByUserId(userId, revokedAt);
    }

    private StoredRefreshToken toDomain(AuthRefreshTokenEntity entity) {
        return new StoredRefreshToken(
                entity.getId(),
                entity.getTokenId(),
                entity.getUser().getId(),
                entity.getExpiresAt(),
                entity.getRevokedAt()
        );
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/persistence/repository/AuthRefreshTokenJpaRepository.java`

```java
package com.dashboardtya.modules.auth.infrastructure.persistence.repository;

import com.dashboardtya.modules.auth.infrastructure.persistence.entity.AuthRefreshTokenEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

public interface AuthRefreshTokenJpaRepository extends JpaRepository<AuthRefreshTokenEntity, UUID> {

    Optional<AuthRefreshTokenEntity> findByTokenId(UUID tokenId);

    @Modifying
    @Query("""
        update AuthRefreshTokenEntity token
           set token.revokedAt = :revokedAt
         where token.tokenId = :tokenId
           and token.revokedAt is null
    """)
    void revokeByTokenId(UUID tokenId, Instant revokedAt);

    @Modifying
    @Query("""
        update AuthRefreshTokenEntity token
           set token.revokedAt = :revokedAt
         where token.user.id = :userId
           and token.revokedAt is null
    """)
    void revokeAllActiveByUserId(UUID userId, Instant revokedAt);
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/persistence/entity/AuthRefreshTokenEntity.java`

```java
package com.dashboardtya.modules.auth.infrastructure.persistence.entity;

import com.dashboardtya.common.persistence.AuditableEntity;
import jakarta.persistence.*;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(
        name = "auth_refresh_tokens",
        uniqueConstraints = {
            @UniqueConstraint(name = "uk_auth_refresh_tokens_token_id", columnNames = "token_id")
        }
)
public class AuthRefreshTokenEntity extends AuditableEntity {

    @Column(name = "token_id", nullable = false, updatable = false)
    private UUID tokenId;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false, foreignKey = @ForeignKey(name = "fk_auth_refresh_tokens_user"))
    private AuthUserEntity user;

    @Column(name = "expires_at", nullable = false)
    private Instant expiresAt;

    @Column(name = "revoked_at")
    private Instant revokedAt;

    public UUID getTokenId() {
        return tokenId;
    }

    public void setTokenId(UUID tokenId) {
        this.tokenId = tokenId;
    }

    public AuthUserEntity getUser() {
        return user;
    }

    public void setUser(AuthUserEntity user) {
        this.user = user;
    }

    public Instant getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(Instant expiresAt) {
        this.expiresAt = expiresAt;
    }

    public Instant getRevokedAt() {
        return revokedAt;
    }

    public void setRevokedAt(Instant revokedAt) {
        this.revokedAt = revokedAt;
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/persistence/AuthUserRepositoryAdapter.java`

```java
package com.dashboardtya.modules.auth.infrastructure.persistence;

import com.dashboardtya.modules.auth.domain.model.AuthUser;
import com.dashboardtya.modules.auth.domain.service.AuthUserRepository;
import com.dashboardtya.modules.auth.infrastructure.persistence.entity.AuthUserEntity;
import com.dashboardtya.modules.auth.infrastructure.persistence.repository.AuthUserJpaRepository;
import org.springframework.stereotype.Component;

import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

@Component
public class AuthUserRepositoryAdapter implements AuthUserRepository {

    private final AuthUserJpaRepository authUserJpaRepository;

    public AuthUserRepositoryAdapter(AuthUserJpaRepository authUserJpaRepository) {
        this.authUserJpaRepository = authUserJpaRepository;
    }

    @Override
    public Optional<AuthUser> findByEmail(String email) {
        return authUserJpaRepository.findByEmailIgnoreCase(normalizeEmail(email))
                .map(this::toDomain);
    }

    @Override
    public Optional<AuthUser> findActiveById(UUID userId) {
        return authUserJpaRepository.findByIdAndActiveTrue(userId)
                .map(this::toDomain);
    }

    @Override
    public boolean existsByEmail(String email) {
        return authUserJpaRepository.existsByEmailIgnoreCase(normalizeEmail(email));
    }

    @Override
    public AuthUser save(AuthUser user) {
        AuthUserEntity entity = new AuthUserEntity();
        entity.setEmail(normalizeEmail(user.email()));
        entity.setFullName(user.fullName());
        entity.setPasswordHash(user.passwordHash());
        entity.setRoleCode(user.roleCode());
        entity.setActive(user.active());

        if (user.id() != null) {
            entity.setId(user.id());
        }

        AuthUserEntity saved = authUserJpaRepository.save(entity);
        return toDomain(saved);
    }

    private AuthUser toDomain(AuthUserEntity entity) {
        return new AuthUser(
                entity.getId(),
                entity.getEmail(),
                entity.getFullName(),
                entity.getPasswordHash(),
                entity.getRoleCode(),
                entity.isActive()
        );
    }

    private String normalizeEmail(String email) {
        return email.trim().toLowerCase(Locale.ROOT);
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/persistence/repository/AuthUserJpaRepository.java`

```java
package com.dashboardtya.modules.auth.infrastructure.persistence.repository;

import com.dashboardtya.modules.auth.infrastructure.persistence.entity.AuthUserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

import java.util.Optional;
import java.util.UUID;

public interface AuthUserJpaRepository extends JpaRepository<AuthUserEntity, UUID>, JpaSpecificationExecutor<AuthUserEntity> {

    Optional<AuthUserEntity> findByEmailIgnoreCase(String email);

    Optional<AuthUserEntity> findByIdAndActiveTrue(UUID id);

    boolean existsByEmailIgnoreCase(String email);
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/infrastructure/persistence/entity/AuthUserEntity.java`

```java
package com.dashboardtya.modules.auth.infrastructure.persistence.entity;

import com.dashboardtya.common.persistence.AuditableEntity;
import com.dashboardtya.modules.access.domain.model.RoleCode;
import jakarta.persistence.*;

@Entity
@Table(
        name = "auth_users",
        uniqueConstraints = {
            @UniqueConstraint(name = "uk_auth_users_email", columnNames = "email")
        }
)
public class AuthUserEntity extends AuditableEntity {

    @Column(name = "email", nullable = false, length = 150)
    private String email;

    @Column(name = "full_name", nullable = false, length = 150)
    private String fullName;

    @Column(name = "password_hash", nullable = false, length = 255)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(name = "role_code", nullable = false, length = 30)
    private RoleCode roleCode;

    @Column(name = "is_active", nullable = false)
    private boolean active;

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getPasswordHash() {
        return passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public RoleCode getRoleCode() {
        return roleCode;
    }

    public void setRoleCode(RoleCode roleCode) {
        this.roleCode = roleCode;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive(boolean active) {
        this.active = active;
    }
}
```

### `backend/src/main/java/com/dashboardtya/common/config/properties/AuthJwtProperties.java`

```java
package com.dashboardtya.common.config.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "auth.jwt")
public class AuthJwtProperties {

    private String secret = "change-me";
    private String issuer = "dashboard-tya";
    private long accessTtlSeconds = 900;
    private long refreshTtlSeconds = 604800;

    public String getSecret() {
        return secret;
    }

    public void setSecret(String secret) {
        this.secret = secret;
    }

    public String getIssuer() {
        return issuer;
    }

    public void setIssuer(String issuer) {
        this.issuer = issuer;
    }

    public long getAccessTtlSeconds() {
        return accessTtlSeconds;
    }

    public void setAccessTtlSeconds(long accessTtlSeconds) {
        this.accessTtlSeconds = accessTtlSeconds;
    }

    public long getRefreshTtlSeconds() {
        return refreshTtlSeconds;
    }

    public void setRefreshTtlSeconds(long refreshTtlSeconds) {
        this.refreshTtlSeconds = refreshTtlSeconds;
    }
}
```

### `backend/src/main/java/com/dashboardtya/common/config/properties/AuthCookieProperties.java`

```java
package com.dashboardtya.common.config.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "auth.cookie")
public class AuthCookieProperties {

    private String name = "refresh_token";
    private String sameSite = "Lax";
    private String domain = "";
    private String path = "/api/auth";
    private String secure = "false";

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSameSite() {
        return sameSite;
    }

    public void setSameSite(String sameSite) {
        this.sameSite = sameSite;
    }

    public String getDomain() {
        return domain;
    }

    public void setDomain(String domain) {
        this.domain = domain;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public String getSecure() {
        return secure;
    }

    public void setSecure(String secure) {
        this.secure = secure;
    }
}
```

### `backend/src/main/java/com/dashboardtya/common/config/CorsConfig.java`

```java
package com.dashboardtya.common.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import com.dashboardtya.common.config.properties.CorsProperties;

@Configuration
public class CorsConfig {

    @Bean
    public CorsConfigurationSource corsConfigurationSource(CorsProperties corsProperties) {
        CorsConfiguration configuration = new CorsConfiguration();

        configuration.setAllowedOrigins(corsProperties.getAllowedOrigins());
        configuration.setAllowedMethods(corsProperties.getAllowedMethods());
        configuration.setAllowedHeaders(corsProperties.getAllowedHeaders());
        configuration.setExposedHeaders(corsProperties.getExposedHeaders());
        configuration.setAllowCredentials(parseBoolean(corsProperties.getAllowCredentials()));

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);

        return source;
    }

    private boolean parseBoolean(String value) {
        if (value == null) {
            return false;
        }
        return "true".equalsIgnoreCase(value) || "1".equals(value);
    }
}
```

### `backend/src/main/java/com/dashboardtya/common/config/properties/CorsProperties.java`

```java
package com.dashboardtya.common.config.properties;

import java.util.ArrayList;
import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "cors")
public class CorsProperties {

    private List<String> allowedOrigins = new ArrayList<>();
    private List<String> allowedMethods = new ArrayList<>();
    private List<String> allowedHeaders = new ArrayList<>();
    private List<String> exposedHeaders = new ArrayList<>();
    private String allowCredentials = "true";

    public List<String> getAllowedOrigins() {
        return allowedOrigins;
    }

    public void setAllowedOrigins(List<String> allowedOrigins) {
        this.allowedOrigins = allowedOrigins;
    }

    public List<String> getAllowedMethods() {
        return allowedMethods;
    }

    public void setAllowedMethods(List<String> allowedMethods) {
        this.allowedMethods = allowedMethods;
    }

    public List<String> getAllowedHeaders() {
        return allowedHeaders;
    }

    public void setAllowedHeaders(List<String> allowedHeaders) {
        this.allowedHeaders = allowedHeaders;
    }

    public List<String> getExposedHeaders() {
        return exposedHeaders;
    }

    public void setExposedHeaders(List<String> exposedHeaders) {
        this.exposedHeaders = exposedHeaders;
    }

    public String getAllowCredentials() {
        return allowCredentials;
    }

    public void setAllowCredentials(String allowCredentials) {
        this.allowCredentials = allowCredentials;
    }
}
```

### `backend/src/main/java/com/dashboardtya/common/web/ApiResponse.java`

```java
package com.dashboardtya.common.web;

public record ApiResponse<T>(
        boolean success,
        String message,
        T data
        ) {

    public static <T> ApiResponse<T> success(String message, T data) {
        return new ApiResponse<>(true, message, data);
    }

    public static <T> ApiResponse<T> failure(String message, T data) {
        return new ApiResponse<>(false, message, data);
    }
}
```

### `backend/src/main/java/com/dashboardtya/modules/auth/api/response/AccessTokenResponse.java`

```java
package com.dashboardtya.modules.auth.api.response;

import com.fasterxml.jackson.annotation.JsonProperty;

public record AccessTokenResponse(
        @JsonProperty("access_token")
        String accessToken,
        @JsonProperty("token_type")
        String tokenType,
        @JsonProperty("expires_in")
        long expiresIn
        ) {

}
```

### `backend/src/main/resources/application.yml`

```yaml
spring:
  application:
    name: ${APP_NAME:dashboard-tya}

  datasource:
    url: jdbc:postgresql://${POSTGRES_HOST:db}:${POSTGRES_PORT:5432}/${POSTGRES_DB:app_db}
    username: ${POSTGRES_USER:app_user}
    password: ${POSTGRES_PASSWORD:app_password}

  jpa:
    open-in-view: false
    hibernate:
      ddl-auto: ${SPRING_JPA_HIBERNATE_DDL_AUTO:update}
    properties:
      hibernate:
        format_sql: true
        jdbc:
          time_zone: ${TZ:America/La_Paz}

  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
    validate-on-migrate: true

  jackson:
    time-zone: ${TZ:America/La_Paz}

server:
  port: ${SERVER_PORT:8000}
  servlet:
    context-path: ${SERVER_CONTEXT_PATH:/api}

management:
  endpoints:
    web:
      exposure:
        include: ${MANAGEMENT_ENDPOINTS_WEB_EXPOSURE_INCLUDE:health,info}
  endpoint:
    health:
      show-details: ${MANAGEMENT_ENDPOINT_HEALTH_SHOW_DETAILS:always}

springdoc:
  swagger-ui:
    path: /swagger-ui.html
    disable-swagger-default-url: true
  api-docs:
    path: /v3/api-docs

logging:
  level:
    root: ${LOG_LEVEL:INFO}

app:
  name: ${APP_NAME:dashboard-tya}
  description: Dashboard de seguimiento de procesos para consultora de recursos humanos
  version: ${APP_VERSION:0.0.1-SNAPSHOT}
  time-zone: ${TZ:America/La_Paz}

cors:
  allowed-origins: ${CORS_ALLOWED_ORIGINS:http://localhost:5173}
  allowed-methods: GET,POST,PUT,PATCH,DELETE,OPTIONS
  allowed-headers: "*"
  exposed-headers: Location,X-Request-Id
  allow-credentials: ${CORS_ALLOW_CREDENTIALS:true}

auth:
  jwt:
    secret: ${AUTH_JWT_SECRET:change-me}
    issuer: ${AUTH_JWT_ISSUER:dashboard-tya}
    access-ttl-seconds: ${AUTH_JWT_ACCESS_TTL_SECONDS:900}
    refresh-ttl-seconds: ${AUTH_JWT_REFRESH_TTL_SECONDS:604800}
  cookie:
    name: ${REFRESH_COOKIE_NAME:refresh_token}
    same-site: ${AUTH_COOKIE_SAME_SITE:Lax}
    domain: ${AUTH_COOKIE_DOMAIN:}
    path: ${AUTH_COOKIE_PATH:/api/auth}
    secure: ${AUTH_COOKIE_SECURE:false}
  bootstrap:
    enabled: ${AUTH_BOOTSTRAP_ENABLED:true}
    admin-email: ${AUTH_BOOTSTRAP_ADMIN_EMAIL:admin@dashboardtya.local}
    admin-password: ${AUTH_BOOTSTRAP_ADMIN_PASSWORD:Admin12345}
    admin-full-name: ${AUTH_BOOTSTRAP_ADMIN_FULL_NAME:Administrador Dashboard}
```

### `backend/src/main/resources/db/migration/V2__create_auth_tables.sql`

```sql
create table if not exists auth_users (
    id uuid primary key,
    email varchar(150) not null,
    full_name varchar(150) not null,
    password_hash varchar(255) not null,
    role_code varchar(30) not null,
    is_active boolean not null default true,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    constraint uk_auth_users_email unique (email),
    constraint ck_auth_users_role_code check (role_code in ('ADMIN', 'ANALYST', 'IT'))
);

create table if not exists auth_refresh_tokens (
    id uuid primary key,
    token_id uuid not null,
    user_id uuid not null,
    expires_at timestamptz not null,
    revoked_at timestamptz null,
    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    constraint uk_auth_refresh_tokens_token_id unique (token_id),
    constraint fk_auth_refresh_tokens_user
        foreign key (user_id) references auth_users(id) on delete cascade
);

create index if not exists idx_auth_refresh_tokens_user_id
    on auth_refresh_tokens(user_id);

create index if not exists idx_auth_refresh_tokens_token_id
    on auth_refresh_tokens(token_id);
```

## Frontend

### `frontend/src/shared/api/http/rawClient.ts`

```ts
import axios from "axios";
import { getEnv } from "@/shared/config/env";

export const rawClient = axios.create({
	// baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
	baseURL: getEnv("ENV_MODE", "/api"),
	withCredentials: true, //  cookie HttpOnly
	headers: {
		"Content-Type": "application/json",
		"X-Requested-With": "XMLHttpRequest", //  CSRF-light
	},
});
```

### `frontend/src/shared/api/http/createHttpClient.ts`

```ts
import axios, { type AxiosInstance, type AxiosError, type InternalAxiosRequestConfig } from "axios";
import { GLOBAL_API_URL } from "@/shared/config";

export type Tokens = {
	accessToken: string;
};

export type RefreshAwareInternalConfig = InternalAxiosRequestConfig & {
	_retry?: boolean;
	_skipRefresh?: boolean;
};

export type HttpClientDeps<E = unknown> = {
	baseURL: string;

	getAccessToken: () => string | null;
	setAccessToken: (token: string) => void;

	clearSession: () => void;

	refreshAccessTokenFn: () => Promise<Tokens>;
	onSessionExpired?: () => void;

	toError: (err: unknown) => E;
};

function setAuthHeader(config: InternalAxiosRequestConfig, token: string) {
	config.headers = config.headers ?? {};
	config.headers.Authorization = `Bearer ${token}`;
}

export function createHttpClient<E = unknown>(deps: HttpClientDeps<E>): AxiosInstance {
	const {
		baseURL,
		getAccessToken,
		setAccessToken,
		clearSession,
		refreshAccessTokenFn,
		onSessionExpired,
		toError,
	} = deps;

	const client = axios.create({
		baseURL,
		timeout: 10_000,
		withCredentials: true, // cookie HttpOnly via navegador
		headers: {
			"Content-Type": "application/json",
			"X-Requested-With": "XMLHttpRequest",
		},
	});

	let isRefreshing = false;
	let queue: Array<(token: string | null) => void> = [];

	const resolveQueue = (token: string | null) => {
		queue.forEach(cb => cb(token));
		queue = [];
	};

	// ----------------------------
	// Request: attach access token
	// ----------------------------
	client.interceptors.request.use(cfg => {
		const config = cfg as RefreshAwareInternalConfig;

		const token = getAccessToken();
		if (token) setAuthHeader(config, token);

		return config;
	});

	// ---------------------------------------
	// Response: refresh on 401 (once per req)
	// ---------------------------------------
	client.interceptors.response.use(
		res => res,
		async (err: unknown) => {
			if (!axios.isAxiosError(err)) return Promise.reject(toError(err));

			const error = err as AxiosError;
			const original = error.config as RefreshAwareInternalConfig | undefined;

			if (!original) return Promise.reject(toError(err));

			const status = error.response?.status;
			if (status !== 401) return Promise.reject(toError(err));

			// no refresh for flagged requests
			if (original._skipRefresh || original._retry) {
				clearSession();
				onSessionExpired?.();
				return Promise.reject(toError(err));
			}

			// avoid loops for auth endpoints
			const url = original.url ?? "";
			if (
				url.includes(GLOBAL_API_URL.login) ||
				url.includes(GLOBAL_API_URL.refresh) ||
				url.includes(GLOBAL_API_URL.logout)
			) {
				clearSession();
				onSessionExpired?.();
				return Promise.reject(toError(err));
			}

			original._retry = true;

			// if refresh in progress, queue this request
			if (isRefreshing) {
				return new Promise((resolve, reject) => {
					queue.push(newToken => {
						if (!newToken) return reject(toError(err));
						setAuthHeader(original, newToken);
						resolve(client(original));
					});
				});
			}

			isRefreshing = true;

			try {
				const { accessToken } = await refreshAccessTokenFn();

				setAccessToken(accessToken);
				resolveQueue(accessToken);

				setAuthHeader(original, accessToken);
				return client(original);
			} catch (refreshErr) {
				resolveQueue(null);
				// Limpia la session y deja unauthenticated
				clearSession();
				onSessionExpired?.();
				return Promise.reject(toError(refreshErr));
			} finally {
				isRefreshing = false;
			}
		},
	);

	return client;
}
```

### `frontend/src/shared/api/http/httpClient.ts`

```ts
import { createHttpClient } from "./createHttpClient";
import { sessionStore } from "@/shared/store/session/model/sessionStore";
import { toAppError } from "@/shared/api/errors";
import { getEnv } from "@/shared/config/env";
import { refreshAccessTokenFn } from "@/shared/store/session/api/refreshSession";


export const httpClient = createHttpClient({
  //baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
  baseURL: getEnv("ENV_MODE", "/api"),

  // Recupera el token de memoria
  getAccessToken: () => sessionStore.getState().accessToken,

  setAccessToken: (token) =>
    sessionStore.getState().setAccessToken(token),

  clearSession: () =>
    sessionStore.getState().clearSession(),

  refreshAccessTokenFn,

  onSessionExpired: () =>
    sessionStore.getState().clearSession(),

  toError: toAppError,
});
```

### `frontend/src/shared/store/session/model/sessionStore.ts`

```ts
import { create } from "zustand";
import type { AppError, AppErrorCode } from "@/shared/api/errors";
import { refreshAccessTokenFn } from "../api/refreshSession";
import { getMe } from "../api/getMe";

/* ============================================================
   TYPES
============================================================ */

export type SessionStatus =
  | "idle"
  | "loading"
  | "authenticated"
  | "unauthenticated";

export type User = {
  id: string;
  email: string;
  name?: string;
  roles?: string[];
  permissions?: string[];
};

export type SessionState = {
  /* ===========================
     STATE
  =========================== */

  status: SessionStatus;
  user: User | null;
  userHydrated: boolean;

  accessToken: string | null;

  lastError: AppError | null;
  lastErrorCode: AppErrorCode | null;

  bootstrapRunId: number;

  /* ===========================
     ACTIONS
  =========================== */

  setAccessToken: (token: string | null) => void;

  hydrateUser: (user: User) => void;

  setStatus: (status: SessionStatus) => void;

  clearSession: () => void;

  bootstrap: () => Promise<void>;
};

/* ============================================================
   STORE
============================================================ */

export const sessionStore = create<SessionState>((set, get) => ({
  status: "idle",
  user: null,
  userHydrated: false,
  accessToken: null,
  lastError: null,
  lastErrorCode: null,
  bootstrapRunId: 0,

  setAccessToken(token) {
    set({ accessToken: token });
  },

  hydrateUser(user) {
    set({
      status: "authenticated",
      user,
      userHydrated: true,
      lastError: null,
      lastErrorCode: null,
    });
  },

  setStatus(status) {
    set({ status });
  },

  clearSession() {
    set({
      status: "unauthenticated",
      user: null,
      userHydrated: false,
      accessToken: null,
      lastError: null,
      lastErrorCode: null,
    });
  },

  async bootstrap() {
    if (get().status === "loading") return;

    const runId = get().bootstrapRunId + 1;

    set({
      status: "loading",
      bootstrapRunId: runId,
      lastError: null,
      lastErrorCode: null,
    });


    try {
      // 1️⃣ refresh vía cookie HttpOnly
      const { accessToken } = await refreshAccessTokenFn();

      if (get().bootstrapRunId !== runId) return;

      get().setAccessToken(accessToken);

      // 2️⃣ obtener usuario
      const me = await getMe();
      console.log("REFRESH USER", me)

      if (get().bootstrapRunId !== runId) return;

      get().hydrateUser({
        id: me.id,
        email: me.email,
        name: me.full_name,
        roles: me.roles ?? [],
        permissions: me.permissions ?? [],
      });

    } catch (e) {
      const err = e as AppError;

      if (get().bootstrapRunId !== runId) return;

      set({
        status: "unauthenticated",
        user: null,
        userHydrated: false,
        accessToken: null,
        lastError: err,
        lastErrorCode: err.code,
      });
    }
  },
}));
```

### `frontend/src/shared/store/session/api/refreshSession.ts`

```ts
import { rawClient } from "@/shared/api/http/rawClient";
import { GLOBAL_API_URL } from "@/shared/config";

export async function refreshAccessTokenFn(): Promise<{ accessToken: string }> {
  const res = await rawClient.post(GLOBAL_API_URL.refresh);
  return { accessToken: res.data.access };
}
```

### `frontend/src/shared/store/session/api/logoutSession.ts`

```ts
import { rawClient } from "@/shared/api/http/rawClient";
import { GLOBAL_API_URL } from "@/shared/config";

/**
 * Backend logout:
 * - borra cookie refresh (HttpOnly)
 * - invalida refresh (si aplicas rotation/blacklist)
 *
 * Nota: este endpoint NO debe depender del access token.
 * Solo requiere la cookie.
 */
export async function logoutSession(): Promise<void> {
  await rawClient.post(GLOBAL_API_URL.logout);
}
```

### `frontend/src/shared/store/session/api/getMe.ts`

```ts
import { httpClient } from "@/shared/api/http/httpClient";
import { GLOBAL_API_URL } from "@/shared/config";

export type MeDto = {
  id: string;
  email: string;
  full_name: string;
  roles: string[];
  permissions: string[];
};

export async function getMe(): Promise<MeDto> {
  const res = await httpClient.get<MeDto>(GLOBAL_API_URL.me);
  return res.data;
}
```

### `frontend/src/features/auth/login-email/api/loginWithEmail.ts`

```ts
import { rawClient } from "@/shared/api/http/rawClient";
import type { LoginRequestDto, LoginResponseDto } from "../model/loginType";
import { GLOBAL_API_URL } from "@/shared/config";

export async function loginWithEmail(payload: LoginRequestDto): Promise<LoginResponseDto> {
  const res = await rawClient.post(GLOBAL_API_URL.login, payload);
  console.log("auth response", res);
  return res.data;
}
```

### `frontend/src/features/auth/login-email/model/useLoginMutation.ts`

```ts
import { useMutation } from "@tanstack/react-query";
import type { AppError } from "@/shared/api/errors";
import { sessionStore } from "@/shared/store/session/model/sessionStore";
import { getMe } from "@/shared/store/session/api/getMe";
import { loginWithEmail } from "../api/loginWithEmail"; // tu API
import type { LoginRequestDto, LoginResponseDto } from "../model/loginType";

export function useLoginMutation() {
  return useMutation<LoginResponseDto, AppError, LoginRequestDto>({
    mutationFn: loginWithEmail,

    onSuccess: async (data) => {
      // 1️⃣ Guardar access en memoria
      sessionStore.getState().setAccessToken(data.accessToken);

      // 2️⃣ Hidratar user
      const me = await getMe();

      console.log("auth me", me)

      sessionStore.getState().hydrateUser({
        id: me.id,
        email: me.email,
        name: me.full_name,
        roles: me.roles ?? [],
        permissions: me.permissions ?? [],
      });
    },
  });
}
```

### `frontend/src/features/auth/login-email/model/loginType.ts`

```ts
/**
 * DTOs for login feature.
 * Keep these aligned with backend contract.
 */

export type LoginRequestDto = {
  email: string;
  password: string;
};

export type LoginResponseDto = {
  accessToken: string;
  expires_in: number;
};
```

### `frontend/src/shared/config/constants/endpoints.ts`

```ts

export const GLOBAL_API_URL = {
  login: "/auth/login",
  me: "/auth/me",
  refresh: "/auth/refresh",
  logout: "/auth/logout",
} as const;

export const PROCESS_ENDPOINTS = {
	list: "/process",
	detail: (processId: string | null) => (processId ? `/process/${processId}`: "/process/:processId"),
} as const;

export const COMPANY_ENDPOINTS = {
	list: "/company",
	detail: (companyId: string | null) => (companyId ? `/company/${companyId}`: "/company/:companyId"),
} as const;

export const VACANCY_ENDPOINTS = {
	list: "/vacancy",
	detail: (vacancyId?: string) => (vacancyId ? `/vacancy/${vacancyId}`: "/vacancy/:vacancyId"),
} as const;
```

## 9. Resumen corto

La implementación de esta app sigue el patrón correcto:

- `access token` corto en `Bearer`
- `refresh token` largo en cookie `HttpOnly`
- refresh token persistido y revocable en DB
- backend stateless con JWT filter
- frontend con interceptor para refresh automático

La parte más importante para que todo funcione bien es mantener alineado el contrato frontend/backend respecto al wrapper `ApiResponse` y al nombre del campo `access_token`.
