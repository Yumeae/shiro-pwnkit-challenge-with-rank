package com.ctf.shiro.config;

import com.ctf.shiro.realm.UserRealm;
import org.apache.shiro.codec.Base64;
import org.apache.shiro.mgt.SecurityManager;
import org.apache.shiro.spring.web.ShiroFilterFactoryBean;
import org.apache.shiro.web.mgt.CookieRememberMeManager;
import org.apache.shiro.web.mgt.DefaultWebSecurityManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.LinkedHashMap;
import java.util.Map;

@Configuration
public class ShiroConfig {

    @Bean
    public UserRealm userRealm() {
        return new UserRealm();
    }

    /**
     * VULNERABILITY: Using the hardcoded default AES key from Shiro <= 1.2.4.
     * This key is public knowledge and allows attackers to craft malicious
     * rememberMe cookies that trigger Java deserialization (CVE-2016-4437).
     */
    @Bean
    public CookieRememberMeManager rememberMeManager() {
        CookieRememberMeManager manager = new CookieRememberMeManager();
        manager.setCipherKey(Base64.decode("kPH+bIxk5D2deZiIxcaaaA=="));
        return manager;
    }

    @Bean
    public DefaultWebSecurityManager securityManager() {
        DefaultWebSecurityManager securityManager = new DefaultWebSecurityManager();
        securityManager.setRealm(userRealm());
        securityManager.setRememberMeManager(rememberMeManager());
        return securityManager;
    }

    @Bean
    public ShiroFilterFactoryBean shiroFilterFactoryBean(SecurityManager securityManager) {
        ShiroFilterFactoryBean filter = new ShiroFilterFactoryBean();
        filter.setSecurityManager(securityManager);
        filter.setLoginUrl("/login");
        filter.setSuccessUrl("/");

        Map<String, String> filterChain = new LinkedHashMap<>();
        filterChain.put("/login", "anon");
        filterChain.put("/static/**", "anon");
        filterChain.put("/**", "user");
        filter.setFilterChainDefinitionMap(filterChain);

        return filter;
    }
}
